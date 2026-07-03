### Title
Token Fee Mis-Accounting in `deposit(address,uint256,string)` Causes Permanent Loss of Token Fees - (File: contracts/pools/RSETHPool.sol)

### Summary
In `RSETHPool.sol` (the Arbitrum L2 pool), the `deposit(address token, uint256 amount, string referralId)` function incorrectly adds the token-denominated fee to `feeEarnedInETH` instead of `feeEarnedInToken[token]`. This mirrors the M-18 class of share/asset mis-accounting: one accounting register is inflated while another is left at zero, causing the protocol to permanently lose token fees and potentially freeze ETH-related operations.

### Finding Description

In `RSETHPool.sol`, the token deposit path computes a fee in token units but credits it to the ETH fee accumulator:

```solidity
// contracts/pools/RSETHPool.sol  lines 284-305
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    if (amount == 0) revert InvalidAmount();
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

    feeEarnedInETH += fee;   // ← BUG: fee is in token units, not ETH

    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

`viewSwapRsETHAmountAndFee(amount, token)` returns `fee = amount * tokenFeeBps[token] / 10_000`, which is denominated in the deposited token (e.g. wstETH), not in ETH. The correct line should be `feeEarnedInToken[token] += fee`.

Because `feeEarnedInToken[token]` is never incremented, the following downstream effects occur:

1. **`withdrawFees(receiver, token)`** reads `feeEarnedInToken[token]` (which stays 0) and transfers nothing — token fees are silently discarded.
2. **`getTokenBalanceMinusFees(token)`** returns `IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token]` = full balance including fees. When `bridgeTokens(token)` is called, the entire token balance (fees included) is bridged to L1, permanently removing the fees from the L2 pool.
3. **`feeEarnedInETH`** is inflated by token-unit amounts. `getETHBalanceMinusFees()` = `address(this).balance - feeEarnedInETH` can underflow (Solidity 0.8 reverts on underflow) once accumulated token fees exceed the ETH balance, bricking `bridgeAssets()` and `withdrawFees(receiver)`.

### Impact Explanation

- **High — Theft of unclaimed yield**: Every token deposit permanently loses its fee. The fee is bridged to L1 as part of the regular token balance rather than being held for the bridger to withdraw. Over time, all token fees are irretrievably sent to L1.
- **Medium — Temporary freezing of funds**: Once `feeEarnedInETH` (inflated by token-unit amounts) exceeds `address(this).balance`, `getETHBalanceMinusFees()` reverts, blocking `bridgeAssets()` and ETH fee withdrawal until an admin manually corrects state.

### Likelihood Explanation

`RSETHPool.sol` is the live Arbitrum pool. Token deposits (e.g. wstETH) are a supported and advertised feature. Every token deposit by any unprivileged user triggers the bug. No special conditions are required; the mis-accounting accumulates monotonically with normal usage.

### Recommendation

Change line 300 of `RSETHPool.sol` from:

```solidity
feeEarnedInETH += fee;
```

to:

```solidity
feeEarnedInToken[token] += fee;
```

This matches the pattern used correctly in the ETH deposit path (`feeEarnedInETH += fee` for ETH deposits) and in all other pool variants (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, etc.).

### Proof of Concept

1. Bridger adds wstETH as a supported token with `tokenFeeBps[wstETH] = 10` (0.1%).
2. Alice calls `deposit(wstETH, 1000e18, "")`.
3. `fee = 1000e18 * 10 / 10_000 = 1e18` (1 wstETH, token units).
4. `feeEarnedInETH += 1e18` — ETH fee register is inflated by 1e18 (wstETH units).
5. `feeEarnedInToken[wstETH]` remains 0.
6. Bridger calls `withdrawFees(receiver, wstETH)` → transfers 0 wstETH. Fee is lost.
7. Bridger calls `bridgeTokens(wstETH)` → `getTokenBalanceMinusFees(wstETH)` = full balance (1000e18 wstETH including the 1e18 fee) → entire balance bridged to L1.
8. After enough token deposits, `feeEarnedInETH` > `address(this).balance` → `getETHBalanceMinusFees()` underflows → `bridgeAssets()` reverts. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPool.sol (L284-305)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPool.sol (L326-347)
```text
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L387-398)
```text
    function getETHBalanceMinusFees() public view returns (uint256) {
        return address(this).balance - feeEarnedInETH;
    }

    /**
     * @dev Get the token balance minus the fees
     * @param token The token address
     * @return The token balance minus the fees
     */
    function getTokenBalanceMinusFees(address token) public view returns (uint256) {
        return IERC20(token).balanceOf(address(this)) - feeEarnedInToken[token];
    }
```

**File:** contracts/pools/RSETHPool.sol (L427-443)
```text
    /// @dev Withdraws fees earned by the pool
    function withdrawFees(
        address receiver,
        address token
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        // withdraw fees in ETH
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);

        emit FeesWithdrawn(amountToSendInToken, token);
    }
```

**File:** contracts/pools/RSETHPool.sol (L543-570)
```text
    /// @dev Bridges tokens to L1 using their corresponding token bridge
    /// @param token The address of the token to bridge
    function bridgeTokens(address token)
        external
        payable
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        if (tokenBridge[token] == address(0)) {
            revert MissingBridgeForToken();
        }

        uint256 balance = getTokenBalanceMinusFees(token);

        if (balance == 0) {
            revert ZeroBridgeAmount();
        }

        // Approve the required amount to the bridge
        IERC20(token).safeIncreaseAllowance(tokenBridge[token], balance);

        // Call the bridge contract to transfer the tokens (msg.value is included in case we need to pay for additional
        // bridging fees)
        IL2TokenBridge(tokenBridge[token]).bridgeTokenToL1{ value: msg.value }(l1VaultETHForL2Chain, balance);

        emit BridgedTokenToL1(token, l1VaultETHForL2Chain, balance);
    }
```

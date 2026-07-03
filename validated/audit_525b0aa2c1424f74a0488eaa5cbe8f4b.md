### Title
Newly Added Tokens in RSETHPool Have Zero Protocol Fee by Default, Allowing Fee-Free Deposits - (File: contracts/pools/RSETHPool.sol)

### Summary
`RSETHPool.addSupportedToken` does not initialize `tokenFeeBps[token]`, leaving it at the Solidity default of `0`. Any user who deposits a newly listed token before the admin separately calls `setTokenFeeBps` pays zero protocol fees, directly analogous to the reported pattern where a user-controlled zero value causes fee computation to produce zero.

### Finding Description
In `RSETHPool`, per-token fee rates are stored in the mapping `tokenFeeBps`:

```solidity
mapping(address token => uint256 feeBps) public tokenFeeBps;
```

When a token is listed via `addSupportedToken`, the function sets the oracle and bridge addresses but never touches `tokenFeeBps[token]`:

```solidity
// contracts/pools/RSETHPool.sol lines 637-656
function addSupportedToken(address token, address oracle, address bridge)
    external onlyRole(TIMELOCK_ROLE)
{
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    // tokenFeeBps[token] is never set — defaults to 0
    emit AddSupportedToken(token, oracle, bridge);
}
```

The fee calculation in `viewSwapRsETHAmountAndFee(amount, token)` reads this uninitialized value:

```solidity
// contracts/pools/RSETHPool.sol lines 335-336
uint256 feeBpsForToken = tokenFeeBps[token];   // == 0
fee = amount * feeBpsForToken / 10_000;         // == 0 for any amount
```

The `deposit(address token, uint256 amount, string referralId)` function uses this result directly:

```solidity
// contracts/pools/RSETHPool.sol lines 298-300
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;   // += 0
```

`setTokenFeeBps` is a completely separate, independently callable function with no coupling to `addSupportedToken`. There is no mechanism that prevents deposits from occurring before it is called.

### Impact Explanation
Every token deposit made between the `addSupportedToken` transaction and the subsequent `setTokenFeeBps` transaction pays zero protocol fees. On Arbitrum (where this contract is deployed), gas costs are negligible, so a user monitoring the chain can deposit arbitrarily large amounts at zero fee cost. The protocol treasury receives no fee revenue for those deposits, constituting theft of unclaimed yield.

**Impact: Low — Contract fails to deliver promised returns (protocol fee collection), but depositor funds are not at risk.**

### Likelihood Explanation
`addSupportedToken` is gated by `TIMELOCK_ROLE`, meaning the listing is publicly visible in the mempool or on-chain before it executes. Any user watching the chain can prepare a deposit transaction to execute immediately after the token is listed. The admin must issue a second, separate transaction (`setTokenFeeBps`) to close the window. Even a short delay (one block on Arbitrum) is exploitable. Likelihood is **Medium** given the predictable, observable trigger.

### Recommendation
- **Short term:** Add a `feeBps` parameter to `addSupportedToken` and set `tokenFeeBps[token] = feeBps` atomically within the same call, before the token becomes depositable.
- **Long term:** Consider enforcing a non-zero minimum fee at the point of token listing, or gating `deposit` on a token until its fee has been explicitly configured (e.g., require `tokenFeeBps[token] > 0` or a separate "fee configured" flag).

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` on `RSETHPool` (Arbitrum). `tokenFeeBps[wstETH]` is `0`.
2. Alice observes the transaction (or the emitted `AddSupportedToken` event).
3. Alice immediately calls `deposit(wstETH, 1_000_000e18, "")`.
4. Inside `viewSwapRsETHAmountAndFee(1_000_000e18, wstETH)`:
   - `feeBpsForToken = tokenFeeBps[wstETH]` → `0`
   - `fee = 1_000_000e18 * 0 / 10_000` → `0`
   - `amountAfterFee = 1_000_000e18`
5. Alice receives the full rsETH equivalent of 1,000,000 wstETH with zero fee paid.
6. Admin later calls `setTokenFeeBps(wstETH, 30)` — but Alice's deposit already settled fee-free.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
    }
```

**File:** contracts/pools/RSETHPool.sol (L637-656)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```

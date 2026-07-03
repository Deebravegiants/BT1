### Title
`swapAssetToPremintedRsETH` Executes While Pool Is Paused — (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol)

### Summary
The `swapAssetToPremintedRsETH` function — the reverse-swap path that drains pool ETH/tokens in exchange for rsETH — is missing the `whenNotPaused` modifier in three production pool contracts. While `deposit` is correctly gated by `whenNotPaused`, the inverse operation is not, allowing the `OPERATOR_ROLE` to move assets out of the pool even during an emergency pause.

### Finding Description
All three pool contracts implement a custom `whenNotPaused` modifier and apply it consistently to user-facing `deposit` functions:

- `RSETHPoolV3.deposit` — `whenNotPaused` present [1](#0-0) 
- `RSETHPoolV3ExternalBridge.deposit` — `whenNotPaused` present [2](#0-1) 
- `RSETHPoolV3WithNativeChainBridge.deposit` — `whenNotPaused` present [3](#0-2) 

However, the operator-only reverse-swap function `swapAssetToPremintedRsETH` carries only `nonReentrant` and `onlyRole(OPERATOR_ROLE)` — no `whenNotPaused`:

- `RSETHPoolV3.swapAssetToPremintedRsETH` [4](#0-3) 
- `RSETHPoolV3ExternalBridge.swapAssetToPremintedRsETH` [5](#0-4) 
- `RSETHPoolV3WithNativeChainBridge.swapAssetToPremintedRsETH` [6](#0-5) 

The function accepts rsETH from the caller, forwards it to the wrapper, and transfers pool-held ETH or ERC-20 tokens (e.g., wstETH) back to the caller: [7](#0-6) 

The `pause` / `unpause` mechanism is defined in each contract: [8](#0-7) 

### Impact Explanation
The pause is the protocol's emergency stop. When it is active, users cannot deposit, but the `OPERATOR_ROLE` can still call `swapAssetToPremintedRsETH` to extract ETH or LSTs from the pool. This asymmetry means the pool's asset base can be reduced while user-facing operations are frozen, undermining the invariant that a pause fully halts fund movement. If the pause was triggered because of an oracle anomaly or a rate-manipulation incident, the operator executing swaps at a stale or manipulated rate during the pause could cause the pool to deliver fewer assets than expected to future users — matching the "contract fails to deliver promised returns" impact tier.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The operator must actively call `swapAssetToPremintedRsETH` while the contract is paused. This is unlikely under normal operations but is a realistic scenario if the operator is unaware that the pause is supposed to block all fund movements, or if operational scripts do not check the paused state before executing. The missing modifier is a code-level omission, not a configuration choice.

**Likelihood: Low.**

### Recommendation
Add `whenNotPaused` to `swapAssetToPremintedRsETH` in all three contracts, consistent with how `deposit` is protected:

```solidity
function swapAssetToPremintedRsETH(
    address rsETH,
    address token,
    uint256 rsETHAmount
)
    external
    nonReentrant
    whenNotPaused          // <-- add this
    onlySupportedTokenOrEth(token)
    onlyRole(OPERATOR_ROLE)
{ ... }
```

### Proof of Concept
1. PAUSER calls `pause()` on `RSETHPoolV3` — `paused` is set to `true`. [9](#0-8) 
2. Any call to `deposit` now reverts with `ContractPaused`. [10](#0-9) 
3. OPERATOR calls `swapAssetToPremintedRsETH(rsETH, ETH_IDENTIFIER, amount)` — the function has no `whenNotPaused` check, so it proceeds, transferring pool ETH to the operator. [11](#0-10) 
4. Pool ETH balance is reduced while users remain locked out, violating the intended invariant of the pause.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L71-74)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-251)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
```

**File:** contracts/pools/RSETHPoolV3.sol (L414-450)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        address token,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlySupportedTokenOrEth(token)
        onlyRole(OPERATOR_ROLE)
    {
        UtilLib.checkNonZeroAddress(rsETH);

        IRsETHTokenWrapper wrapper = IRsETHTokenWrapper(address(wrsETH));
        IERC20 tokenContract = IERC20(token);

        if (!wrapper.allowedTokens(rsETH)) revert TokenNotAllowedInWrapper();
        if (rsETHAmount == 0) revert InvalidAmount();
        if (rsETHAmount > wrapper.maxAmountToDepositBridgerAsset(rsETH)) revert ExceedsMaxAmountToDepositInWrapper();

        // Get the amount of token to transfer to the user for the given amount of rsETH provided
        uint256 tokenAmount = viewSwapAssetToPremintedRsETH(token, rsETHAmount);

        // Transfer rsETH from sender to the wrapper
        IERC20(rsETH).safeTransferFrom(msg.sender, address(wrapper), rsETHAmount);

        // Transfer the token from the pool to the sender
        if (token == ETH_IDENTIFIER) {
            if (getETHBalanceMinusFees() < tokenAmount) revert InsufficientETHBalanceForReverseSwap();
            (bool success,) = payable(msg.sender).call{ value: tokenAmount }("");
            if (!success) revert TransferFailed();
        } else {
            if (getTokenBalanceMinusFees(token) < tokenAmount) revert InsufficientAssetBalanceForReverseSwap();
            tokenContract.safeTransfer(msg.sender, tokenAmount);
        }

        emit ReverseSwapOccurred(msg.sender, rsETH, token, rsETHAmount, tokenAmount);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L591-601)
```text
    /// @dev Pauses the pausable methods in the contract
    function pause() external onlyRole(PAUSER_ROLE) whenNotPaused {
        paused = true;
        emit Paused(msg.sender);
    }

    /// @dev Unpauses the pausable methods in the contract
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) whenPaused {
        paused = false;
        emit Unpaused(msg.sender);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-372)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L578-587)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        address token,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlySupportedTokenOrEth(token)
        onlyRole(OPERATOR_ROLE)
    {
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-287)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L448-457)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        address token,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlySupportedTokenOrEth(token)
        onlyRole(OPERATOR_ROLE)
    {
```

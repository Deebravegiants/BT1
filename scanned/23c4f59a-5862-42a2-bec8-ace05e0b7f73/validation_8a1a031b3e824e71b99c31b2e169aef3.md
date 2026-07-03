### Title
Missing `whenNotPaused` on `swapAssetToPremintedRsETH()` Allows Whitelisted Users to Bypass Emergency Stop - (File: contracts/pools/RSETHPoolV2ExternalBridge.sol)

### Summary
`RSETHPoolV2ExternalBridge` implements a custom pause mechanism (`bool public paused`) and a `whenNotPaused` modifier, but the `swapAssetToPremintedRsETH()` function — callable by any address holding `WHITELISTED_USER_ROLE` — is not guarded by `whenNotPaused`. When the contract is paused in an emergency, whitelisted users can still invoke this function to extract ETH from the pool in exchange for rsETH, defeating the purpose of the emergency stop.

### Finding Description
`RSETHPoolV2ExternalBridge` defines a `paused` state variable and a `whenNotPaused` modifier: [1](#0-0) 

The `deposit()` function is correctly guarded: [2](#0-1) 

However, `swapAssetToPremintedRsETH()` — which transfers ETH from the pool to the caller — is **not** guarded by `whenNotPaused`: [3](#0-2) 

The access modifier `onlyOperatorOrWhitelisted` explicitly allows `WHITELISTED_USER_ROLE` holders — external, non-operator users — to call this function: [4](#0-3) 

The function body transfers ETH out of the pool to the caller: [5](#0-4) 

### Impact Explanation
When the pauser triggers `pause()` in response to an emergency (e.g., oracle manipulation, bridge exploit, or price anomaly), the intent is to halt all fund movements. Because `swapAssetToPremintedRsETH()` lacks `whenNotPaused`, any address holding `WHITELISTED_USER_ROLE` can continue to drain ETH from the pool by providing rsETH. The ETH balance of the pool — accumulated from user deposits — can be extracted while the contract is supposed to be frozen. This constitutes a **temporary freezing of funds bypass** (Medium impact per scope).

### Likelihood Explanation
`WHITELISTED_USER_ROLE` is a role granted by the admin to external users (distinct from `OPERATOR_ROLE`). Once granted, these users can call `swapAssetToPremintedRsETH()` at any time, including during a pause. The pause is designed as a rapid emergency response; revoking individual role grants is a slower, separate action. Any whitelisted user — whether acting opportunistically or as a compromised account — can exploit this window. No admin collusion is required; the role was legitimately granted prior to the emergency.

### Recommendation
Add the `whenNotPaused` modifier to `swapAssetToPremintedRsETH()` in `RSETHPoolV2ExternalBridge.sol`, consistent with how `deposit()` is protected:

```solidity
function swapAssetToPremintedRsETH(
    address rsETH,
    uint256 rsETHAmount
)
    external
    nonReentrant
    whenNotPaused                          // <-- add this
    onlyOperatorOrWhitelisted(msg.sender)
{
```

### Proof of Concept
1. Admin calls `pause()` on `RSETHPoolV2ExternalBridge` in response to an incident.
2. `paused` is set to `true`; `deposit()` now reverts for all callers.
3. A whitelisted user (holding `WHITELISTED_USER_ROLE`) calls `swapAssetToPremintedRsETH(rsETH, rsETHAmount)`.
4. The `onlyOperatorOrWhitelisted` modifier passes; `whenNotPaused` is never checked.
5. The function transfers `rsETHAmount` of rsETH from the caller to the wrapper and sends the equivalent ETH from the pool to the caller.
6. ETH is extracted from the paused pool, bypassing the emergency stop. [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L92-95)
```text
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L130-135)
```text
    modifier onlyOperatorOrWhitelisted(address account) {
        if (!hasRole(OPERATOR_ROLE, account) && !hasRole(WHITELISTED_USER_ROLE, account)) {
            revert NotOperatorOrWhitelisted();
        }
        _;
    }
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-289)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L418-446)
```text
    function swapAssetToPremintedRsETH(
        address rsETH,
        uint256 rsETHAmount
    )
        external
        nonReentrant
        onlyOperatorOrWhitelisted(msg.sender)
    {
        UtilLib.checkNonZeroAddress(rsETH);

        IRsETHTokenWrapper wrapper = IRsETHTokenWrapper(address(wrsETH));

        if (!wrapper.allowedTokens(rsETH)) revert TokenNotAllowedInWrapper();
        if (rsETHAmount == 0) revert InvalidAmount();
        if (rsETHAmount > wrapper.maxAmountToDepositBridgerAsset(rsETH)) revert ExceedsMaxAmountToDepositInWrapper();

        // Get the amount of ETH to transfer to the user for the given amount of rsETH provided
        uint256 ethAmount = viewSwapAssetToPremintedRsETH(rsETHAmount);

        // Transfer rsETH from sender to the wrapper
        IERC20(rsETH).safeTransferFrom(msg.sender, address(wrapper), rsETHAmount);

        // Transfer the ETH from the pool to the sender
        if (getETHBalanceMinusFees() < ethAmount) revert InsufficientETHBalanceForReverseSwap();
        (bool success,) = payable(msg.sender).call{ value: ethAmount }("");
        if (!success) revert TransferFailed();

        emit ReverseSwapOccurred(msg.sender, rsETH, rsETHAmount, ethAmount);
    }
```

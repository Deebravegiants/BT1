Audit Report

## Title
Missing `+ amount` in ETH Branch of Deposit Limit Check Allows ETH Deposits to Exceed the Cap - (File: `contracts/LRTDepositPool.sol`)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` evaluates the ETH deposit limit using only the pre-existing total (`totalAssetDeposits > limit`) rather than including the incoming deposit (`totalAssetDeposits + amount > limit`). The LST branch applies the correct arithmetic. As a result, any ETH depositor can push the pool's ETH balance above the governance-configured `depositLimitByAsset` cap, violating the protocol's intended risk invariant.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the function branches on whether the asset is `ETH_TOKEN`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // ← missing `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

The ETH branch returns `true` only when the total *already* exceeds the limit before the deposit is applied. It never evaluates whether the incoming `amount` would push the total over the limit. The LST branch correctly adds `amount` to the pre-deposit total.

The call chain is:
- `depositETH` (lines 76–93) — `external payable`, no role restriction — calls `_beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected)`.
- `_beforeDeposit` (lines 648–670) calls `_checkIfDepositAmountExceedesCurrentLimit` and reverts with `MaximumDepositLimitReached` only when it returns `true`.
- Because the ETH branch never includes `amount`, the revert never fires for a deposit that merely *crosses* the limit; it only fires if the limit was already crossed in a prior transaction.

No other guard in `depositETH` or `_beforeDeposit` enforces the deposit cap for ETH.

## Impact Explanation
**Low — Contract fails to deliver promised returns.**

`depositLimitByAsset` is a protocol-enforced risk cap governing maximum EigenLayer exposure per asset. For ETH, this cap is not enforced at the boundary: a depositor can submit any ETH amount that brings the running total from below the cap to above it, and the protocol will mint rsETH for the full amount and accept the ETH. The cap is only enforced once the total has already crossed it in a prior block. No direct theft of funds occurs, but the protocol accepts more ETH than governance intended, violating the stated invariant.

## Likelihood Explanation
The entry point `depositETH` is permissionless and requires no special role. The vulnerable condition arises whenever `totalAssetDeposits` is below the configured limit — a normal operational state for any active pool. Any depositor who observes the current total approaching the cap can trivially submit a deposit that exceeds it. The condition is repeatable across blocks as long as the total has not already crossed the limit.

## Recommendation
Add `+ amount` to the ETH branch to match the LST branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The ETH-specific branch is unnecessary once corrected and can be removed entirely.

## Proof of Concept
1. Governance sets `depositLimitByAsset(ETH_TOKEN) = 1000 ether`.
2. `getTotalAssetDeposits(ETH_TOKEN)` returns `999 ether`.
3. An LST depositor attempting to deposit 2 ETH-equivalent is blocked: `999 + 2 > 1000 → true → MaximumDepositLimitReached`.
4. An ETH depositor calls `depositETH{value: 2 ether}(0, "")`:
   - `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 2 ether)` evaluates `999 > 1000 → false`.
   - No revert; rsETH is minted for 2 ETH.
   - `totalAssetDeposits(ETH_TOKEN)` is now `1001 ether`, 1 ETH above the cap.
5. The depositor can repeat this in subsequent blocks for arbitrarily large amounts as long as the running total has not already crossed the limit in a prior block.

**Foundry test plan:** Deploy `LRTDepositPool` on a local fork, configure `depositLimitByAsset(ETH_TOKEN) = 1000 ether`, seed the pool to `999 ether` via prior deposits, then call `depositETH{value: 2 ether}` from an unprivileged address and assert that `getTotalAssetDeposits(ETH_TOKEN) > 1000 ether` and no revert occurred. Contrast with an equivalent `depositAsset` call for an LST that reverts with `MaximumDepositLimitReached`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L676-682)
```text
    function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (asset == LRTConstants.ETH_TOKEN) {
            return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
        }
        return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
    }
```

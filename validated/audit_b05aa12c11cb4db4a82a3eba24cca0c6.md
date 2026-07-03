The code at lines 676-682 exactly matches the claim. The ETH branch at line 679 uses `totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)` (ignoring `amount`), while the ERC20 branch at line 681 correctly uses `totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)`. The `_beforeDeposit` guard at line 661 is the sole caller, and `getAssetCurrentLimit` at line 404 uses the same `>` operator, confirming the public API signals "full" while the guard still admits one more ETH deposit.

Audit Report

## Title
ETH Deposit Limit Check Excludes New Deposit Amount, Allowing Limit Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` omits the incoming `amount` from the ETH branch comparison, checking only whether the pre-deposit total already exceeds the cap. When `totalAssetDeposits == depositLimitByAsset`, the guard returns `false` and the deposit proceeds, pushing the total above the configured ceiling. The equivalent ERC20 path correctly includes `amount` in the comparison.

## Finding Description
In `contracts/LRTDepositPool.sol` at lines 676–682, the function branches on asset type:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount ignored
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // amount included
}
```

When `totalAssetDeposits == depositLimit`, the ETH expression `totalAssetDeposits > depositLimit` evaluates to `false`, so `_beforeDeposit` (lines 648–670) does not revert via `MaximumDepositLimitReached`, and the deposit is accepted. After the call, `totalAssetDeposits` exceeds the cap by the full deposit amount. `getAssetCurrentLimit` (lines 402–409) already returns `0` in this state (using the same `>` operator), so the public view correctly signals no remaining capacity while the internal guard still admits the deposit — a direct inconsistency between the view layer and the execution layer.

## Impact Explanation
**Low. Contract fails to deliver promised returns, but doesn't lose value.** The deposit limit is a governance-set risk-management ceiling bounding the protocol's EigenLayer slashing exposure. Bypassing it for ETH allows one deposit of arbitrary size beyond the cap, minting rsETH in excess of the intended ceiling and staking more ETH in EigenLayer than governance authorized. No user funds are stolen or frozen, but the protocol fails to enforce its own stated deposit ceiling for ETH, which is a concrete failure to deliver a promised protocol invariant.

## Likelihood Explanation
**Medium.** The condition is reached whenever `getTotalAssetDeposits(ETH_TOKEN)` equals `depositLimitByAsset[ETH_TOKEN]`. Any unprivileged depositor can trigger this by being the depositor that fills the pool to exactly the cap, or by observing on-chain state and submitting a deposit at that moment. No special role, privilege, or front-running is required — only a standard `depositETH` call.

## Recommendation
Remove the ETH-specific branch and unify the logic to always include `amount`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

This matches the existing ERC20 path and makes the guard consistent with `getAssetCurrentLimit`.

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Users deposit ETH until `getTotalAssetDeposits(ETH_TOKEN) == 1000 ether`.
3. `getAssetCurrentLimit(ETH_TOKEN)` returns `0` — public API signals cap is full.
4. Attacker calls `depositETH{value: 500 ether}(0, "")`.
5. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `1000 ether > 1000 ether` → `false` → no revert.
6. `_mintRsETH` mints rsETH for 500 ETH; `getTotalAssetDeposits(ETH_TOKEN)` becomes `1500 ether`, 50% above the cap.
7. The excess ETH is forwarded to NodeDelegators and staked in EigenLayer beyond the intended risk ceiling.

**Foundry test plan:** Deploy `LRTDepositPool` with a mock `lrtConfig` returning `depositLimitByAsset = 1000 ether`. Call `depositETH` in a loop until `getTotalAssetDeposits == 1000 ether`. Assert `getAssetCurrentLimit == 0`. Then call `depositETH{value: 1 ether}` and assert it does **not** revert (demonstrating the bypass). Assert `getTotalAssetDeposits == 1001 ether` post-call. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L402-409)
```text
    function getAssetCurrentLimit(address asset) public view override returns (uint256) {
        uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
        if (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)) {
            return 0;
        }

        return lrtConfig.depositLimitByAsset(asset) - totalAssetDeposits;
    }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
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

The code at lines 676-682 exactly matches the claim. The ETH branch omits `amount` from the comparison, `_beforeDeposit` is the sole caller, and `getAssetCurrentLimit` already signals zero capacity at the boundary — confirming the inconsistency is real and reachable.

---

Audit Report

## Title
ETH Deposit Limit Check Excludes Incoming Amount, Allowing One-Deposit Bypass - (File: contracts/LRTDepositPool.sol)

## Summary
`_checkIfDepositAmountExceedesCurrentLimit` uses a strict greater-than comparison on the pre-deposit total for ETH, omitting the incoming `amount`, while ERC20 assets correctly include `amount` in the comparison. When `totalAssetDeposits` equals the configured cap, the ETH guard returns `false` and the deposit is accepted, pushing total deposits above the cap by the full deposit amount.

## Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` (L676-682) branches on asset type:

```solidity
// L678-681
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // amount ignored
}
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // amount included
```

When `totalAssetDeposits == depositLimit`, the ETH expression evaluates `depositLimit > depositLimit` → `false`, so `_beforeDeposit` (L661-663) does not revert and the deposit proceeds. After the call, `getTotalAssetDeposits(ETH_TOKEN)` exceeds the cap by the full deposit amount.

`getAssetCurrentLimit` (L402-409) uses the same `>` operator and correctly returns `0` when `totalAssetDeposits == depositLimit`, meaning the public view API already signals no remaining capacity while the internal guard still admits one more deposit of unbounded size. `_beforeDeposit` is the sole caller of this guard and is invoked by both `depositETH` and `depositAsset`.

## Impact Explanation
**Low. Contract fails to deliver promised returns, but doesn't lose value.** The deposit limit is a governance-set risk-management ceiling bounding EigenLayer slashing exposure. Bypassing it for ETH allows one additional deposit of arbitrary size beyond the cap, minting rsETH in excess of the intended ceiling and staking more ETH in EigenLayer than governance authorized. No funds are directly stolen or frozen, but the protocol fails to enforce its own stated deposit ceiling for ETH.

## Likelihood Explanation
**Medium.** The condition is reached whenever `totalAssetDeposits` for ETH equals `depositLimitByAsset`. Any unprivileged depositor can trigger this by being the last depositor to fill the pool to exactly the cap, or by observing on-chain state and submitting a deposit at that moment. No special role, flash loan, or front-running is required — only a public `depositETH` call.

## Recommendation
Include the incoming deposit amount in the ETH branch, matching the ERC20 logic:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

## Proof of Concept
1. Admin sets `depositLimitByAsset[ETH_TOKEN] = 1000 ether`.
2. Users deposit until `getTotalAssetDeposits(ETH_TOKEN) == 1000 ether`.
3. `getAssetCurrentLimit(ETH_TOKEN)` returns `0` — public API signals cap is full.
4. Attacker calls `depositETH{value: 500 ether}(0, "")`.
5. Inside `_checkIfDepositAmountExceedesCurrentLimit`: `1000 ether > 1000 ether` → `false` → no revert.
6. `_mintRsETH` mints rsETH for 500 ETH; `getTotalAssetDeposits(ETH_TOKEN)` becomes `1500 ether`, 50% above cap.
7. Excess ETH is forwarded to NodeDelegators and staked in EigenLayer beyond the intended risk ceiling.

**Foundry test plan:** Deploy pool, set limit to `1000 ether`, deposit `1000 ether` via multiple calls, assert `getAssetCurrentLimit == 0`, then call `depositETH{value: 1 ether}` and assert it does not revert and `getTotalAssetDeposits > depositLimitByAsset`. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/LRTDepositPool.sol (L648-663)
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

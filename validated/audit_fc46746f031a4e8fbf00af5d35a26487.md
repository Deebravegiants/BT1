### Title
ETH Deposit Limit Bypass Due to Missing `amount` in Limit Check - (File: contracts/LRTDepositPool.sol)

### Summary
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the ETH branch omits the incoming deposit `amount` from the cap comparison. Any unprivileged depositor can therefore push total ETH deposits arbitrarily beyond the configured `depositLimitByAsset` in a single transaction, while the identical check for ERC-20 assets correctly includes `amount`.

### Finding Description
`_checkIfDepositAmountExceedesCurrentLimit` (lines 676–682) contains two branches:

```solidity
// ETH branch — amount is MISSING
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));   // line 679
}
// ERC-20 branch — amount is correctly included
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // line 681
```

For ETH the guard only fires when the running total **already** exceeds the cap. It never checks whether the new deposit would push the total over the cap. A depositor who calls `depositETH` while `totalAssetDeposits == depositLimit - 1 wei` can supply any `msg.value` and the check returns `false` (not exceeded), minting rsETH for the full amount.

The external report's root cause — a transaction `amount` field that is silently omitted from an accounting check — maps exactly to this omission of the `amount` parameter in the ETH deposit-limit guard.

### Impact Explanation
The ETH deposit cap is a protocol-level risk control. Bypassing it allows rsETH to be minted against more ETH collateral than the protocol intends to accept, breaking the invariant that `getTotalAssetDeposits(ETH) ≤ depositLimitByAsset(ETH)`. If the cap is set to bound EigenLayer exposure or liquidity risk, a single large deposit can push the protocol into an over-exposed state, potentially leading to protocol insolvency or inability to honour withdrawals — **Medium: Temporary freezing of funds / Low: Contract fails to deliver promised returns**.

### Likelihood Explanation
The entry point is the public, permissionless `depositETH` function. No special role, governance action, or precondition beyond having ETH is required. Any depositor can trigger this in a single transaction whenever `totalAssetDeposits ≤ depositLimitByAsset(ETH)`, which is the normal operating state of the protocol. Likelihood is **High**.

### Recommendation
Add `amount` to the ETH branch, mirroring the ERC-20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

### Proof of Concept
1. Assume `depositLimitByAsset(ETH_TOKEN) = 1000 ETH` and `getTotalAssetDeposits(ETH_TOKEN) = 999 ETH`.
2. Attacker calls `depositETH{value: 500 ETH}(0, "")`.
3. `_checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, 500 ETH)` evaluates `999 ETH > 1000 ETH` → `false` → no revert.
4. `_mintRsETH` mints rsETH for 500 ETH; total ETH deposits become 1499 ETH, 49.9 % above the cap.
5. For comparison, a 500-token ERC-20 deposit under the same conditions would evaluate `999 + 500 > 1000` → `true` → `MaximumDepositLimitReached` revert. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTDepositPool.sol (L86-92)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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

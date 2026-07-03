### Title
ETH Deposit Limit Bypass via Missing Amount in Boundary Check - (File: contracts/LRTDepositPool.sol)

### Summary
The `_checkIfDepositAmountExceedesCurrentLimit` function applies an asymmetric and incomplete boundary check for ETH deposits: it omits the incoming `amount` from the comparison and uses a strict `>` instead of `>=`. As a result, the ETH deposit cap is entirely unenforced — any depositor can push the protocol's ETH holdings arbitrarily beyond the configured limit in a single transaction.

### Finding Description
In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`, the check for LST assets correctly adds the incoming deposit amount before comparing against the limit:

```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

But the ETH branch silently drops `amount` from the expression:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

Two compounding defects are present:

1. **Missing `amount`**: The function receives `amount` (equal to `msg.value`) but never uses it in the ETH branch. The check only asks "has the limit already been exceeded?" — not "would this deposit exceed the limit?"
2. **Strict `>` instead of `>=`**: Even if `totalAssetDeposits` exactly equals `depositLimitByAsset`, the condition evaluates to `false`, so the deposit is still permitted.

The caller is `_beforeDeposit`, which reverts only when `_checkIfDepositAmountExceedesCurrentLimit` returns `true`: [2](#0-1) 

`depositETH` passes `msg.value` as `depositAmount` into `_beforeDeposit`, which forwards it as `amount` to the limit check — but the ETH branch ignores it entirely. [3](#0-2) 

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

The deposit cap is a protocol-level risk parameter set by the admin to bound exposure to a single asset class. With the ETH branch broken, any depositor can mint rsETH against an arbitrarily large ETH deposit in a single call, as long as `totalAssetDeposits ≤ depositLimitByAsset` at the moment of the call. The protocol accumulates ETH far beyond the intended ceiling, undermining the risk management guarantee the limit is meant to provide. No direct theft occurs, but the contract fails to enforce its own stated constraint.

### Likelihood Explanation
High. The entry path is the public, permissionless `depositETH` function. No special role, flash loan, or oracle manipulation is required. Any depositor who observes that the current ETH total has not yet crossed the limit can immediately exploit this by sending a single large ETH deposit.

### Recommendation
Add `amount` to the ETH branch and use `>=` to match the semantics of the LST branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount >= lrtConfig.depositLimitByAsset(asset));
}
```

This mirrors the fix described in the reference report (changing `>` to `>=`) and additionally closes the missing-amount gap that is unique to the ETH path.

### Proof of Concept

1. Admin sets `depositLimitByAsset[ETH] = 100 ether`.
2. Current `totalAssetDeposits(ETH) = 50 ether`.
3. Attacker calls `depositETH{value: 10_000 ether}(0, "")`.
4. Inside `_checkIfDepositAmountExceedesCurrentLimit(ETH, 10_000 ether)`:
   - `totalAssetDeposits = 50 ether`
   - ETH branch: `return (50 ether > 100 ether)` → `false`
   - `amount = 10_000 ether` is never evaluated.
5. `_beforeDeposit` does **not** revert; rsETH is minted for 10,000 ETH.
6. After the call, `totalAssetDeposits(ETH) = 10,050 ether` — 100× the intended cap. [4](#0-3)

### Citations

**File:** contracts/LRTDepositPool.sol (L86-93)
```text
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

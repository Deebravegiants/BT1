### Title
Wrong Guard Condition for ETH Deposit Limit Allows Limit to Be Exceeded - (File: contracts/LRTDepositPool.sol)

---

### Summary

`LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit` uses an incorrect guard condition for ETH deposits. The ETH branch omits the incoming deposit `amount` from the comparison, meaning the deposit limit can be breached by any depositor as long as the current total has not already crossed the cap.

---

### Finding Description

The function `_checkIfDepositAmountExceedesCurrentLimit` is the sole guard that enforces the per-asset deposit cap before minting rsETH. It is called from `_beforeDeposit`, which is invoked by both `depositETH` and `depositAsset`.

For ERC-20 assets the guard is correct:

```solidity
return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
```

For ETH the `amount` parameter is silently dropped:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));
}
``` [1](#0-0) 

Because `amount` is never added to `totalAssetDeposits` in the ETH branch, the check only fires when the cap is **already** exceeded, not when the incoming deposit **would** exceed it. Any depositor can therefore push the ETH total above the configured limit by up to one full deposit amount in a single transaction.

The guard is invoked unconditionally before every ETH deposit: [2](#0-1) 

and the deposit proceeds to mint rsETH proportional to the full `msg.value` even when the limit is breached: [3](#0-2) 

---

### Impact Explanation

The ETH deposit cap (`depositLimitByAsset[ETH_TOKEN]`) is the protocol's primary mechanism for bounding total ETH exposure. When it is bypassable, the protocol accepts and mints rsETH against more ETH than governance has authorised. This directly violates the protocol's promised deposit ceiling and can cause rsETH to be minted beyond the intended supply cap, degrading the backing ratio for all rsETH holders.

**Impact**: Low — Contract fails to deliver promised returns (deposit limit not enforced for ETH), but deposited ETH is not directly stolen.

---

### Likelihood Explanation

The entry path is fully permissionless: any address can call `depositETH` with `msg.value` that would push the total above the limit. No special role, front-running, or external dependency is required. The condition is triggered whenever `totalAssetDeposits` is within one deposit of the cap, which is a normal operating state.

**Likelihood**: High.

---

### Recommendation

Apply the same guard logic used for ERC-20 tokens to the ETH branch:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

The special-casing of `ETH_TOKEN` is unnecessary and is the root cause of the bug.

---

### Proof of Concept

Assume:
- `depositLimitByAsset[ETH_TOKEN] = 100 ether`
- `getTotalAssetDeposits(ETH_TOKEN)` currently returns `99 ether`

**ERC-20 path** (correct): `99 + 10 = 109 > 100` → reverts with `MaximumDepositLimitReached`.

**ETH path** (buggy): `99 > 100` → `false` → no revert → 10 ETH is accepted and rsETH is minted, pushing the total to 109 ETH — 9 ETH above the configured cap. [1](#0-0)

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

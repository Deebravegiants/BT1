### Title
ETH Deposit Limit Check Omits New Deposit Amount, Allowing Limit Bypass — (File: contracts/LRTDepositPool.sol)

---

### Summary

`_checkIfDepositAmountExceedesCurrentLimit` applies inconsistent validation logic for ETH versus ERC20 assets. The ETH branch checks only whether the *current* total already exceeds the limit, without including the incoming deposit amount. Any depositor can push ETH deposits past the configured cap by exactly one deposit.

---

### Finding Description

In `LRTDepositPool._checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// contracts/LRTDepositPool.sol
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset)); // ← no `+ amount`
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset)); // ← correct
}
```

For ERC20 assets the guard is `totalAssetDeposits + amount > limit`, which correctly blocks any deposit that would push the total over the cap. For ETH the guard is `totalAssetDeposits > limit`, which only fires when the cap is *already* exceeded. When `totalAssetDeposits == limit` the ETH branch returns `false`, the deposit proceeds, and the post-deposit total becomes `limit + msg.value`.

This is called unconditionally from `_beforeDeposit`, which is invoked by the public `depositETH` entry point:

```solidity
// contracts/LRTDepositPool.sol
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [1](#0-0) [2](#0-1) 

---

### Impact Explanation

The deposit limit is the protocol's primary mechanism for capping exposure to any single asset. Bypassing it for ETH means the protocol can accumulate more ETH than the admin intended, violating the invariant that `getTotalAssetDeposits(ETH_TOKEN) ≤ depositLimitByAsset(ETH_TOKEN)`. No funds are directly stolen, but the contract fails to deliver the promised deposit-cap guarantee.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

The condition is trivially reachable: any unprivileged depositor who calls `depositETH` when `totalAssetDeposits == depositLimit` triggers the bypass. No special timing, front-running, or privileged access is required. The entry path is fully public.

---

### Recommendation

Apply the same `+ amount` inclusion to the ETH branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
```

---

### Proof of Concept

1. Admin sets ETH deposit limit to `100 ether` via `updateAssetDepositLimit`.
2. Cumulative ETH deposits reach exactly `100 ether` (`totalAssetDeposits == 100 ether`).
3. Alice calls `depositETH{value: 1 ether}(minRSETH, "")`.
4. `_checkIfDepositAmountExceedesCurrentLimit` evaluates `100 ether > 100 ether` → `false` → no revert.
5. `_mintRsETH` mints rsETH for Alice; total ETH deposits become `101 ether`, exceeding the cap.
6. The `MaximumDepositLimitReached` guard is never triggered despite the limit being breached. [1](#0-0) [3](#0-2)

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

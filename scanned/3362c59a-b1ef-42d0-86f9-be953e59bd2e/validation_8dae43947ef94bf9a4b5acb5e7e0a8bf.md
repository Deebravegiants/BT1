### Title
Ineffective ETH Deposit Limit Check Allows Depositors to Exceed Protocol Cap - (File: contracts/LRTDepositPool.sol)

---

### Summary
`_checkIfDepositAmountExceedesCurrentLimit` in `LRTDepositPool.sol` applies an asymmetric guard: for ERC20 assets it correctly includes the incoming deposit amount in the limit comparison, but for ETH it omits it entirely. The ETH branch check is therefore ineffective — it never blocks a deposit that would push the total above the cap, only one where the total is already above it.

---

### Finding Description
The vulnerability class from the reference report is an **ineffective guard**: a `require` check that is supposed to protect logic but fails to do so because of how the arithmetic is structured. The analog here is structurally identical.

In `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    if (asset == LRTConstants.ETH_TOKEN) {
        return (totalAssetDeposits > lrtConfig.depositLimitByAsset(asset));  // ← amount omitted
    }
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));  // ← correct for ERC20
}
``` [1](#0-0) 

For ETH, the check evaluates `totalAssetDeposits > depositLimit`. Because `amount` is not added, the check returns `false` (i.e., "not exceeded") whenever `totalAssetDeposits <= depositLimit`, regardless of how large `amount` is. The guard is supposed to block deposits that would push the total over the cap, but it only blocks deposits made after the cap is already breached — which is the same logical failure as the reference report's always-true `require`.

This function is called directly from `_beforeDeposit`, which gates every `depositETH` call:

```solidity
if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
    revert MaximumDepositLimitReached();
}
``` [2](#0-1) 

---

### Impact Explanation
Any unprivileged depositor can call `depositETH` and deposit an arbitrarily large amount of ETH as long as `totalAssetDeposits <= depositLimit` at the time of the call. The ETH deposit cap is not enforced. This causes the protocol to mint rsETH beyond the intended ceiling, violating the protocol's promised deposit limit invariant.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation
The entry path is `depositETH` — a public, permissionless function callable by any user. No special role, front-running, or external dependency is required. The condition (`totalAssetDeposits <= depositLimit`) is the normal operating state of the protocol. Likelihood is **High**.

---

### Recommendation
Add `amount` to the ETH branch to match the ERC20 branch:

```solidity
if (asset == LRTConstants.ETH_TOKEN) {
    return (totalAssetDeposits + amount > lrtConfig.depositLimitByAsset(asset));
}
``` [3](#0-2) 

---

### Proof of Concept

1. Assume `depositLimitByAsset(ETH) = 1000 ether` and `getTotalAssetDeposits(ETH) = 1000 ether` (exactly at cap).
2. Attacker calls `depositETH{value: 500 ether}(0, "")`.
3. `_checkIfDepositAmountExceedesCurrentLimit(ETH, 500 ether)` evaluates `1000 ether > 1000 ether` → `false`.
4. `_beforeDeposit` does **not** revert; rsETH is minted for 500 ETH.
5. `getTotalAssetDeposits(ETH)` is now `1500 ether`, 50% above the configured cap.
6. The same call can be repeated by any depositor in the same block, with no bound on the overshoot. [4](#0-3)

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

### Title
Mismatched Units Between Minimum Deposit and Minimum Withdrawal Thresholds Can Permanently Freeze User rsETH - (`contracts/LRTWithdrawalManager.sol` / `contracts/LRTDepositPool.sol`)

---

### Summary

`LRTDepositPool` enforces a minimum deposit in **ETH/asset terms** (`minAmountToDeposit`), while `LRTWithdrawalManager` enforces a minimum withdrawal in **rsETH terms** (`minRsEthAmountToWithdraw[asset]`). Because rsETH accrues value over time (price > 1 ETH per rsETH), a user depositing exactly `minAmountToDeposit` ETH receives fewer rsETH tokens than `minAmountToDeposit` in raw number terms. If `minRsEthAmountToWithdraw[asset]` is set equal to or greater than `minAmountToDeposit`, the user's rsETH balance falls below the withdrawal minimum. When `LRTDepositPool` is subsequently paused or the deposit limit is reached, the user cannot top up, permanently freezing their funds.

---

### Finding Description

`LRTDepositPool._beforeDeposit()` enforces:

```solidity
if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
    revert InvalidAmountToDeposit();
}
``` [1](#0-0) 

Here `depositAmount` is denominated in **ETH or LST asset units**.

`LRTWithdrawalManager.initiateWithdrawal()` enforces:

```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
``` [2](#0-1) 

Here `rsETHUnstaked` is denominated in **rsETH token units**. The same check applies to `instantWithdrawal()`: [3](#0-2) 

Both `minAmountToDeposit` and `minRsEthAmountToWithdraw[asset]` are set independently by the LRT admin with no enforced relationship between them: [4](#0-3) [5](#0-4) 

The rsETH exchange rate starts at 1 ETH/rsETH and grows as EigenLayer rewards accrue. Therefore, depositing `X` ETH yields `X / rsETHPrice` rsETH, which is strictly less than `X` whenever `rsETHPrice > 1`. If the admin sets both minimums to the same nominal value (e.g., `0.05`), a user depositing exactly `0.05 ETH` receives approximately `0.05 / 1.1 ≈ 0.04545 rsETH` — below the `0.05 rsETH` withdrawal minimum. The user cannot withdraw, and if `LRTDepositPool` is paused (`whenNotPaused` on `depositETH`) or the per-asset deposit cap is hit (`MaximumDepositLimitReached`), the user cannot top up either. [6](#0-5) [7](#0-6) 

---

### Impact Explanation

A user who deposits exactly `minAmountToDeposit` ETH (the protocol-advertised minimum) receives rsETH below `minRsEthAmountToWithdraw[asset]`. Both `initiateWithdrawal` and `instantWithdrawal` revert. If `LRTDepositPool` is paused or the deposit cap is exhausted, the user has no path to recover their funds. This constitutes **permanent freezing of user funds** (Critical).

---

### Likelihood Explanation

The scenario requires two concurrent conditions:

1. **Admin sets both minimums to the same nominal value** — a natural and likely configuration mistake given the values appear to represent the same concept ("minimum amount") but are in different units.
2. **`LRTDepositPool` is paused or deposit limit is reached** — both are normal operational events; the contract has a `PAUSER_ROLE` and per-asset deposit caps enforced on-chain.

The rsETH price diverges from 1:1 immediately after launch as rewards accrue, making the unit mismatch active from early in the protocol's life. The likelihood is **medium to high** given the naturalness of the misconfiguration.

---

### Recommendation

Enforce a consistent relationship between the two minimums. The simplest fix is to express `minRsEthAmountToWithdraw[asset]` in terms of the equivalent ETH value at the time of the check, or to validate in `setMinRsEthAmountToWithdraw` that the rsETH minimum corresponds to no more than `minAmountToDeposit` ETH at the current oracle price. Alternatively, remove the minimum withdrawal check and rely solely on the deposit minimum, ensuring users can always exit any position they were permitted to enter.

---

### Proof of Concept

```
Setup:
  minAmountToDeposit         = 0.05 ETH   (set by LRT admin in LRTDepositPool)
  minRsEthAmountToWithdraw   = 0.05 rsETH (set by LRT admin in LRTWithdrawalManager for ETH asset)
  rsETH oracle price         = 1.10 ETH per rsETH (realistic after rewards accrue)

Step 1 — Alice deposits the protocol minimum:
  Alice calls LRTDepositPool.depositETH{value: 0.05 ETH}(0, "")
  rsethAmountToMint = 0.05 ETH / 1.10 ETH·rsETH⁻¹ ≈ 0.04545 rsETH
  → Alice holds 0.04545 rsETH

Step 2 — LRT admin (or PAUSER_ROLE) pauses LRTDepositPool:
  LRTDepositPool.pause()
  → depositETH() now reverts with "Pausable: paused"

Step 3 — Alice tries to withdraw:
  Alice calls LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, 0.04545e18, "")
  → 0.04545 rsETH < 0.05 rsETH minimum → revert InvalidAmountToWithdraw()

Step 4 — Alice tries to top up to meet the withdrawal minimum:
  Alice calls LRTDepositPool.depositETH{value: 0.01 ETH}(0, "")
  → revert "Pausable: paused"

Result: Alice's 0.04545 rsETH (≈ 0.05 ETH in value) is permanently frozen.
```

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

**File:** contracts/LRTDepositPool.sol (L282-285)
```text
    function setMinAmountToDeposit(uint256 minAmountToDeposit_) external onlyLRTAdmin {
        minAmountToDeposit = minAmountToDeposit_;
        emit MinAmountToDepositUpdated(minAmountToDeposit_);
    }
```

**File:** contracts/LRTDepositPool.sol (L657-659)
```text
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }
```

**File:** contracts/LRTDepositPool.sol (L661-663)
```text
        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L162-164)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L224-226)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L330-332)
```text
    function setMinRsEthAmountToWithdraw(address asset, uint256 minRsEthAmountToWithdraw_) external onlyLRTAdmin {
        minRsEthAmountToWithdraw[asset] = minRsEthAmountToWithdraw_;
        emit MinAmountToWithdrawUpdated(asset, minRsEthAmountToWithdraw_);
```

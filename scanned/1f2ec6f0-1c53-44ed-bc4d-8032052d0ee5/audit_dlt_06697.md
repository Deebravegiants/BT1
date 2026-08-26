# [M] Deposit will revert incorrectly because of a wrong calculation in the dloopdepositor Base

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-19
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/149
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x08dac082505c12fca15b4e2efb048c21935fddc09ee6a82b88f381e2f35ba36b
  **Severity:** medium
  
  **Description:**
  **Description**\


When users deposit with a flashloan, the system uses the **target leverage** (like 3x) to guess how much debt token will be needed. But in reality, the vault uses the **current leverage** (like 2.85x or 3.15x) to decide how much to borrow.

This causes a problem.

If the current leverage is close to 3x but not exact (say 2.85x), the system borrows **less** debt token than expected. So, when it checks if enough debt was received to repay the flashloan (including fee), it wrongly thinks it wasn’t enough — and the deposit fails, even though it actually could repay.

---

### 🧨 **Why This Happens**

* Flashloan code assumes leverage is always **3x**.
* Actual borrow uses the **current leverage** (e.g., 2.85x).
* So it borrows **less**, which triggers this bad check:

  ```solidity
  if (debtReceived < debtSwappedIn + fee) revert();
  ```

Even though the vault has enough to pay back the loan, this check fails because it was expecting more.




  ```solidity

  function _deposit(
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/149_

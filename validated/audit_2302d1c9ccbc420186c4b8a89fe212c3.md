### Title
`_withdrawFromAave` Becomes Non-Functional After All Principal Is Withdrawn, Causing ETH Withdrawal Failures — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary
The `_withdrawFromAave` internal function silently returns 0 (no-op) when `totalETHDepositedToAave == 0`, even when aWETH balance (accrued interest) remains in the contract. This mirrors the M-02 pattern exactly: a function that becomes non-functional after a monotonically-decreasing counter reaches zero, causing a dependent user-facing path to permanently revert until operator intervention.

---

### Finding Description

`_withdrawFromAave` caps the withdrawable amount at `totalETHDepositedToAave` (tracked principal):

```solidity
uint256 withdrawabl
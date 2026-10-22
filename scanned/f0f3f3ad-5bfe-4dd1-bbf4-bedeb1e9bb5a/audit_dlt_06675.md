# [H] Missing Handling of Excess Ether in buy() Function

## Summary
Severity: High
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/8
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/johny37)

  **Beneficiary:** 0x083A4CeA5cBF6dBFE8c6040787280d01D24aDDB9
  **Submission hash (on-chain):** 0x238a0152d16bc3f5f92ce6eb468dc3e878da3aa48a205199be850811bd9a1def
  **Severity:** high
  
  **Description:**
  **Description**\

The buy() function currently enforces require(msg.value >= totalRoseAmount), ensuring that the sent Ether is at least the required amount (token purchase plus fee). However, the contract does not handle the scenario where msg.value is greater than totalRoseAmount. There is no mechanism to return or otherwise manage surplus Ether. As a result, if a user inadvertently sends more Ether than needed, those excess funds simply remain in the contract.

**Attack Scenario**\

A user tries to buy tokens and miscalculates the fee or total purchase cost, sending more Ether than required.
The transaction succeeds, but the user has overpaid—the contract does not return or utilize the excess amount.
This effectively causes a user-fund loss (or at best, a donation to the contract), without a clear mechanism for recovery.

**Attachments**

1. **Revised Code File (Optional)**

Exact Match: Use require(msg.value == totalRoseAmount), ensuring users send precisely the correct amount.

Partial Refund: If msg.value > totalRoseAmount, automatically refund the difference to the buyer.

# [M] No Time Checks During invest()

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/34
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/johny37)

  **Beneficiary:** 0x083A4CeA5cBF6dBFE8c6040787280d01D24aDDB9
  **Submission hash (on-chain):** 0x31ad16974b2f11329dd09f8eded16f04252a7fe632faa5a0dc10850d1abd21d7
  **Severity:** medium
  
  **Description:**
  **Description**\

The contract defines a startTime and endTime for the sale, but the invest() function—despite being central to recording contributions—does not enforce any time-based restrictions. The owner can update investor balances at any point in time, including before the startTime or after the endTime.


**Attachments**

If you intend to restrict investments to a specific window:

```solidity
require(block.timestamp >= startTime && block.timestamp <= endTime, "Sale not active");
```
Add this require statement inside the invest() function to enforce that contributions are only recorded between startTime and endTime.

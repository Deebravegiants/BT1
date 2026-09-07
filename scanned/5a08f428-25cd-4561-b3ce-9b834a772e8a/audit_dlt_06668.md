# [M] Unbounded investors array with duplicate entries will cause transferDSS() to fail

## Summary
Severity: Medium
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/35
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** 0xInAllHonesty
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/InAllHonesty)

  **Beneficiary:** 0x53a956a6dAcA04e552Cb0285F56eA68eB49C1bcC
  **Submission hash (on-chain):** 0x7acf6980d1a932b35f5da20bb5cf63e71e9aa3dd4dd67a94d5120b068830fe82
  **Severity:** medium
  
  **Description:**
  **Description**\

The `CrowdFunding` contract stores all investors in an array that is used to distribute tokens in the `transferDSS()` function. This implementation has two critical issues:

1. The investors array can contain duplicate addresses since there's no check when adding new investors in the invest() function. This means the same investor could receive their tokens multiple times in transferDSS(), potentially draining more tokens than they should receive.
2. The transferDSS() function iterates through the entire investors array in a single transaction to distribute tokens. As the array grows with more investors, the gas cost of this operation increases linearly.


**Attack Scenario**\

1. Attacker makes multiple small investments through different transactions
2. Each investment adds their address again to the investors array
3. After many transactions, their address appears hundreds of times in the array
4. When transferDSS() is called, either:
  a) The function reverts due to exceeding block gas limit, preventing any token distribution
  b) If it doesn't revert, **the attacker receives their tokens multiple times**

The issue is particularly severe because:
- There's no way to remove addresses from the array
- The contract owner can't selectively distribute tokens - it's all or nothing
- Once the array grows too large, the contract becomes permanently unable to fulfill its core purpose of token distribution


**Attachments**

1. **Proof of Concept (PoC) File**


2. **Revised Code File (Optional)**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/35_

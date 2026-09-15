# [H] Divide-before-multiply

## Summary
Severity: High
Chain: Smart contract
Component: DAOsis
Published: 2025-01-28
Source: https://github.com/hats-finance/DAOsis-0x8ef21ecb2af12ce9cc0e475eec25f90a9622b4f4/issues/16
Type: hats-finding

## Details
**Github username:** @0xjarix
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xjarix)

  **Beneficiary:** 0xd95ea3d35D5B4AB1DecAA33610192dc7F459cdcf
  **Submission hash (on-chain):** 0x36ebfb70e7727e2146d099c56385b177b12aa34175aaf4fc23d477565b36e876
  **Severity:** high
  
  **Description:**
  **Description**\
Describe the context and the effect of the vulnerability.
Loss of precision when investing in Exchange

**Attack Scenario**\
Describe how the vulnerability can be exploited.
When owner calls `Exchange::invest(...)`
`tokensToReceive` and `totalTokensSold` will be updated wrongly because of a loss of precision in this LOC
`uint256 tokenAmount = (amount / tokenPrice) * 1e18;`
when owner will call `transferDSS(...)` it will transfer less than possible, the user will lose funds
**Attachments**
1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
- `uint256 tokenAmount = (amount * 1e18) / tokenPrice;`

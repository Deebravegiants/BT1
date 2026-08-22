# [H] One or more UNTRUSTED & malicious arbitrary users could intentionally slash VALID messages and potentially cause 51% attack scenario.

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-10
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/46
Type: hats-finding

## Details
**Github username:** @dappconsulting
**Twitter username:** 0xSCSamurai
**Submission hash (on-chain):** 0x49f154c607f7c7870030cacb54ac91f1f2aa50539d2804e4bd41298b3e785144
**Severity:** high

**Description:**
**Description**\

`HashThreshold::slashSigners()` - One or more UNTRUSTED & malicious arbitrary users could intentionally slash VALID messages and potentially cause 51% attack scenario.

https://github.com/Layr-Labs/eigenlayer-contracts/blob/8cad6a1d9c7b3df2c84c9984603d7904bd88d766/src/contracts/middleware/example/HashThreshold.sol#L99-L115
https://github.com/Layr-Labs/eigenlayer-contracts/blob/ed3a1515db04ae75dd5e267425ba5aca314fe062/src/contracts/core/Slasher.sol#L100-L106

**Attack Scenario**\

There is no access control in below function, which would allow for malicious actors to call this function repeatedly targeting as many different VALID messages and validators as possible, with the potential to successfully carry out a 51% attack, resulting in temporary(at best) or permanent(at worst) DoS of critical protocol functionalities, as well as potential for financial losses for both validators and users.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
  
**Files:**
  - slashing_51%_attack.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmWK5g1SzMexeKSJrkHa9FiXaZ11K1qesnA53dw571qoH1)
  - slashing_51%_attack_mitigation.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmbtsdXFYWxVRaYCCm4KoBco2qYZAH3a1USmq6VjttiA8C)

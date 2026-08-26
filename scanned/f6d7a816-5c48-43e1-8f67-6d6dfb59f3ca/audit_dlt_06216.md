# [M] Signature Malleability in ercrecover() function in RegulationsManagerV2.sol::recoverSigner()

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-09
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/36
Type: hats-finding

## Details
**Github username:** @erictee2802
**Submission hash (on-chain):** 0x4019ad4d7e70f094a7cd557d3d392bff8d0f53f1854511eb96a4bbc88bc4d82f
**Severity:** medium

**Description:**
**Description**\
EVM's ecrecover is susceptible to signature malleability which allows replay attacks, please refer to this document for more info: https://swcregistry.io/docs/SWC-117/




**Attack Scenario**\
Signature malleability might leads to replay attacks.


**Attachments**

1. **Proof of Concept (PoC) File**
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/RegulationsManagerV2.sol#L76


2. **Revised Code File (Optional)**

3. **Recommendations**\
Consider using OpenZeppelin’s ECDSA library:https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol

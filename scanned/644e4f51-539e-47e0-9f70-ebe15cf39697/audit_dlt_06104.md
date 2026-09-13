# [H] Signature malleability in `permit` function

## Summary
Severity: High
Chain: Smart contract
Component: VMEX
Published: 2023-06-22
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/44
Type: hats-finding

## Details
**Github username:** --
**Submission hash (on-chain):** 0xe3c62c6546edd8b652a731dbcbaff6f24d971a29fe18cdbb29ce88ff9487b030
**Severity:** high severity

**Description:**
## Impact
The function `permit` contains a vulnerability in its signature verification process that can result in signature collisions. This vulnerability arises due to the symmetrical nature of the elliptic curve used for signatures in Ethereum. As a consequence, multiple valid signatures can produce the same outcome without requiring the possession of the private key. Attackers can exploit this vulnerability to manipulate contract behavior and bypass security measures.

## POC

The function aims to implement a cryptographic signature system for verifying signatures in Ethereum contracts. However, it fails to consider the uniqueness of signatures, assuming that a valid signature is always unique. This assumption can lead to severe security vulnerabilities.

The vulnerability allows an attacker to create alternative signatures that, when verified, produce the same valid result as the original signature. Consequently, an attacker can replace a legitimate signature with a colliding signature, potentially bypassing security checks and altering contract behavior.

The vulnerability arises from the fact that for every [v,r,s] there exists another [v,r,s] that returns the same valid result. This symmetrical property of the elliptic curve used for signatures in Ethereum can be exploited by an attacker to craft alternative signatures that resemble with the original one. This resembling signatures, while different from the original, can still produce the same valid result during signature verification.

For more details about how this may cause problem in this function you can check these 3 links below:
https://swcregistry.io/docs/SWC-117
https://swcregistry.io/docs/SWC-121
https://medium.com/immunefi/intro-to-cryptography-and-signatures-in-ethereum-2025b6a4a33d

By leveraging signature resemblance, an attacker can manipulate the behavior of the delegateBySig function and potentially bypass security checks. They can remake a valid signature causing the function to accept the colliding signature as legitimate, leading to unintended delegation of authority or unauthorized access to certain functionalities..

## Recommended Mitigation Steps
The easiest and simplest way to prevent this kind of attacks happen is using OpenZeppelin’s ECDSA.sol version 4.7.3 or greater(older versions have bugs in the implementation).

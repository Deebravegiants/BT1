# [M] `Address.isContract`

## Summary
Severity: Medium
Contest weight: 0.1812
Dataset id: 17172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from the contract’s reliance on the OpenZeppelin helper Address.isContract to enforce that the _eoaRepresentative argument is an externally owned account (EOA). The check is implemented as require(!Address.isContract(_eoaRepresentative),"Only EOA representative permitted") inside the registerBLSPublicKeys function. This assumption is flawed because Address.isContract determines contract status by inspecting the code size at the target address, which is zero while a contract is being constructed and also zero for an address that has been pre‑computed but not yet deployed (for example via CREATE2). Consequently an attacker can supply the address of a contract that is either in its constructor phase or that will be deployed later, and the require statement will incorrectly evaluate to true, allowing the registration to succeed. An adversary can therefore register a malicious contract as the representative, bypassing the intended EOA‑only restriction. The protocol later treats this representative as a trustworthy EOA, which may enable the contract to execute arbitrary logic, intercept or redirect funds, or otherwise violate the business logic that assumes a simple user‑controlled account. The impact is that the protocol’s security model is broken: funds may be drained, voting or staking rights may be hijacked, and users may see their expected refunds or rewards disappear because the malicious representative can manipulate the protocol state. This condition occurs only when the registration function is called with an address that either belongs to a contract under construction or to a contract whose address has been predicted with CREATE2 before deployment. The issue was discovered during a manual audit that examined the semantics of the isContract check and identified edge‑case scenarios where the check can be bypassed. It is difficult to notice because the isContract helper is widely trusted and the bypass requires only timing the call during construction or using a deterministic address, which does not raise obvious runtime errors. To remediate, the protocol should stop relying on Address.isContract to enforce EOA status. Instead, the design should assume that the representative may be a contract and enforce security through other means such as signature verification, role‑based access control, or explicit whitelisting. Removing the require statement or replacing it with a more robust verification eliminates the false sense of security and aligns the implementation with the reality that contract addresses cannot be reliably distinguished from EOAs at registration time. From a user’s perspective, a participant who expects that only personal wallets can be registered may instead see a contract address accepted, leading to unexpected behavior such as missing refunds, zero balances, or funds being transferred to an unknown contract, which contradicts the expectation that only their personal account can act as a representative.

## Proof of Concept
When BLS public key is registered in `registerBLSPublicKeys()`, it has the check of
`require(!Address.isContract(_eoaRepresentative), "Only EOA representative permitted")`

However, this check can be passed even though input is a smart contract if

1. Function is called in the constructor. `Address.isContract()` checks for the code length, but during construction code length is 0.
2. Smart contract that has not been deployed yet can be used. The CREATE2 opcode can be used to deterministically calculate the address of a smart contract before it is created. This means that the user can bypass this check by calling this function before deploying the contract.

## Recommendation
It is generally not recommended to enforce an address to be only EOA and AFAIK, this is impossible to enforce due to the aforementioned cases. I recommend the protocol team to take a closer look at this and build the protocol with the assumption that `_eoaRepresentative == EOA`.

Using tx.origin is generally frowned upon.

The sponsor confirming that they know it’s an issue does not invalidate it as an issue.

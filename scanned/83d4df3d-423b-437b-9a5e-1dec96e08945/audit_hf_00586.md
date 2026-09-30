# [M] createProject can be frontrun

## Summary
Severity: Medium
Contest weight: 0.3959
Dataset id: 2062
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the public function createProject, which allows any external address to invoke it without any form of authentication or pre‑approval. Because the contract does not restrict who may call createProject, a malicious actor can observe a legitimate user's pending transaction, submit the same call with their own parameters (or the same parameters) in a separate transaction with a higher gas price, and therefore be mined first. This front‑running attack results in the attacker being recorded as the owner of the newly created collection. As the owner, the attacker gains the permission to withdraw the paymentToken associated with that collection, effectively stealing funds that were intended for the legitimate project creator. The issue also extends to the _collections.isForSale flag, which can be altered by the frontrunner before the original transaction is processed, further compromising the sale logic. The problem occurs whenever createProject is called in an environment where transactions are publicly visible and miners can prioritize higher‑fee submissions, which is the default behavior of most EVM‑compatible blockchains. All users who rely on the contract to securely register projects and collections are affected, as they may lose ownership rights and associated token balances. The flaw was identified during a manual security audit that highlighted the lack of access control and the potential for race conditions inherent in public transaction ordering. It can be difficult to notice because the contract will still execute successfully from the perspective of the blockchain, but the business logic—ownership assignment—does not match the expectation of the original caller, leading to silent loss of funds. To remediate, the contract should enforce an allow‑list or whitelist for authorized project creators, and/or require the caller to provide a signed message proving that the address they intend to act as matches msg.sender, using a cryptographic signature verification (e.g., OpenZeppelin's ECDSA). This moves the vulnerability from an unauthorized access and front‑running class of bug to a properly authenticated operation, restoring the intended invariant that only the intended creator can become the owner of a collection and withdraw its payment tokens. From a user’s point of view, the symptom is that after creating a project they see the collection listed under another address, receive no payment token, or notice that their balance has been reduced to zero despite having performed the creation step. The expectation that they would become the owner and retain control over the collection is violated, breaking the accounting guarantees of the platform.

## Proof of Concept
```solidity
1. Anyone can call `createProject`.

function createProject(
    string memory _projectId,
    Collection[] memory _collections
) external onlyAvailableProject(_projectId) {
    require(
        _collections.length > 0,
        'CoreFactory: should have more at least one collection'
    );
```

## Recommendation
Two ways to mitigate.
  1. Consider use white list on project creation.
  2. Ask user to sign their address and check the signature against `msg.sender`. <https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol#L102>

This is an issue and we intend to fix it!

The solutions listed in #34 and #35 are better.

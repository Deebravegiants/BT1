# [H] Reentrancy in Account initialization can be used to drain creditors funds

## Summary
Severity: High
Contest weight: 0.7116
Dataset id: 3037
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a reentrancy flaw in the account initialization routine of the Arcadia protocol. When a new account is created through Factory.createAccount, the factory deploys a proxy, records the account, mints an NFT, and then calls IAccount.initialize on the newly deployed proxy. Inside AccountV1.initialize the contract first performs some checks, assigns owner and registry, optionally opens a margin sub‑account for a creditor, and only after those steps sets the internal reentrancy flag locked to 1. Because the flag is set after the call to _openMarginAccount, which is an external call to a creditor‑controlled contract, the contract is effectively unlocked during that call. An attacker who can control the creditor address can craft a malicious contract that, when invoked by _openMarginAccount, re‑enters the initialization flow or calls other privileged functions before the guard is engaged. By re‑entering, the attacker can repeatedly invoke the margin‑opening logic or withdraw funds, ultimately draining the creditor’s balance from the newly created account. The issue manifests when a creditor is specified during account creation; if the creditor is a malicious contract, the external call provides a re‑entrancy window. Users see the expected NFT minted but later notice that the creditor’s funds are missing or that the account balance becomes zero despite a successful creation. The bug is hard to notice because the re‑entrancy guard appears to be set, yet it is set too late, and the external call is hidden inside the initialization logic. The flaw was discovered during a manual security audit that inspected the order of state changes and external calls. To remediate, the contract should enable the re‑entrancy guard before any external call, i.e., set locked = 1 (or use OpenZeppelin’s nonReentrant modifier) at the beginning of initialize, or restructure the logic so that no external calls occur while the contract is in an unlocked state. This class of bug belongs to the broader category of “re‑entrancy during initialization” where state‑changing guards are applied after vulnerable external interactions, breaking the intended accounting guarantees of the protocol.

## Recommendation
Change the order of operations so the reentrancy guard is enabled during ini-
tialization:

```solidity

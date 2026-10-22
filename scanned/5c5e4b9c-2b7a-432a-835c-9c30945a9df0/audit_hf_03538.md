# [C] GLOBAL-1 | Malicious User Drains CrossChainRelay

## Summary
Severity: Critical
Contest weight: 0.0735
Dataset id: 19338
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service (DoS) condition caused by the absence of a minimum deposit amount check in the Vault contract. Because the deposit function accepts any non‑negative value, a malicious actor can submit a large number of deposits with trivial or zero ether. Each deposit triggers the Vault to forward the received ether to the CrossChainRelay component, which holds the protocol’s pooled ether for cross‑chain operations. By repeatedly invoking the deposit with minimal amounts, the attacker can exhaust the ether balance of the CrossChainRelay, effectively draining the pool and preventing any further legitimate cross‑chain transactions. This situation arises whenever the contract’s deposit logic does not enforce a lower bound on the transferred value, a condition that is easy to overlook because small deposits appear harmless and do not raise immediate alarms. The impact is that funds disappear from the relay, users attempting to withdraw or perform cross‑chain actions receive no ether, and the overall system may halt because the relay can no longer fulfill its role. The issue was identified during a security audit that examined the Vault’s input validation and discovered that no guard clause exists to reject deposits below a sensible threshold. The problem is subtle because the contract still functions correctly for normal‑sized deposits, and the malicious activity can be hidden among many legitimate tiny deposits, making it difficult to detect through ordinary monitoring. To remediate the flaw, the Vault should enforce a minimum deposit amount (for example, a non‑zero value or a protocol‑defined floor) and optionally implement rate‑limiting or deposit‑size checks to make mass spamming economically infeasible. By adding this validation, the contract will reject trivial deposits, preventing an attacker from draining the CrossChainRelay and preserving the expected accounting guarantees of the protocol.

## Recommendation
Implement a minimum deposit amount in the Vault contract such that DoS attacks like this one become unfeasible.

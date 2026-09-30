# [M] HermesVault incident: HermesVault, an Algorand-based privacy protocol using zero-knowledge proofs for private transactions, was exploited. The attacker

## Summary
Severity: Medium
Target: HermesVault
Loss: $ 29,466
Attack method: Smart Contract Vulnerability
Published: 2026-05-19
Source: https://x.com/giuliopizzini/status/2056858969403183292?referrer=grok-com
Type: slowmist-incident

## Details
HermesVault, an Algorand-based privacy protocol using zero-knowledge proofs for private transactions, was exploited. The attacker exploited a flaw in the key reset defense logic within the withdrawal verification script. This allowed bypassing the zero-knowledge (zk) verification process and unauthorized withdrawal of funds. The protocol permanently shut down operations following the incident. Lead engineer Giulio Pizzini confirmed that the core zk circuit remained secure, but the auxiliary withdrawal script had a vulnerability. The team patched the issue, refunded a large portion of the funds, and initiated a full refund process for affected users.

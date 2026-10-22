# [M] Ether.fi Liquid incident: Users of ether.fi Liquid (liquidETH) lost ~15.45 ETH after an attacker exploited missing access control in AtomicQueue.solve() on

## Summary
Severity: Medium
Target: Ether.fi Liquid
Loss: $ 38130
Attack method: Smart Contract Vulnerability
Published: 2026-09-11
Source: https://x.com/SlowMist_Team/status/2098344499923784048
Type: slowmist-incident

## Details
Users of ether.fi Liquid (liquidETH) lost ~15.45 ETH after an attacker exploited missing access control in AtomicQueue.solve() on the caller-supplied solver parameter. The attacker crafted a malicious AtomicRequest, forced already-approved victim addresses to act as solver, and drained funds via existing ERC-20 allowances with transferFrom. About 11 users were affected.

# [M] Scallop incident: A deprecated side contract (V2 rewards contract) tied to Scallop’s sSUI Spool rewards pool was exploited. The attacker exploited a

## Summary
Severity: Medium
Target: Scallop
Loss: $ 142,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-26
Source: https://x.com/Scallop_io/status/2048976878997041499
Type: slowmist-incident

## Details
A deprecated side contract (V2 rewards contract) tied to Scallop’s sSUI Spool rewards pool was exploited. The attacker exploited a missing validation in the reward accumulator logic (uninitialized variable in update_points function). By staking a small amount (0.2 SUI), they generated massive fake reward points (162 trillion), draining the entire leftover rewards pool of approximately 150,000 SUI. Core lending markets, user deposits, and active pools were unaffected. The team promptly froze the affected contract, committed to covering 100% of the loss from treasury, and resumed normal operations.

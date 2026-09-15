# [M] Juicebox V3 incident: Juicebox V3 (via its REVLoans borrowing extension) was exploited through a borrowFrom Spoof Attack. The vulnerability stemmed from

## Summary
Severity: Medium
Target: Juicebox V3
Loss: $ 52,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-20
Source: https://academy.teleswap.xyz/defi-protocol-hacks-april-2026-exploits-analyzed/
Type: slowmist-incident

## Details
Juicebox V3 (via its REVLoans borrowing extension) was exploited through a borrowFrom Spoof Attack. The vulnerability stemmed from insufficient validation in the borrowFrom function, particularly the caller-supplied "source" parameter (a REVLoanSource struct with .terminal and .token). This allowed forging an accounting context; when currency matched the destination, the protocol skipped the oracle and used attacker-controlled decimals/balances, enabling borrowing at an inflated share price. The attack used two transactions (one to seed fake accounting, one to drain against a legitimate terminal), draining approximately 21.77 ETH (worth ~$52,000).

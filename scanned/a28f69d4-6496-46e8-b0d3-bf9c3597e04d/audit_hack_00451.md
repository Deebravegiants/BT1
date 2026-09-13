# [M] SQ Protocol incident: On May 12, 2026, at approximately 10:11 UTC, the SQ Protocol on BNB Chain was exploited for $346,137. The attacker abused a hardco

## Summary
Severity: Medium
Target: SQ Protocol
Loss: $ 346,100
Attack method: Smart Contract Vulnerability
Published: 2026-05-12
Source: https://x.com/Defi_Nerd_sec/status/2054425936746148148
Type: slowmist-incident

## Details
On May 12, 2026, at approximately 10:11 UTC, the SQ Protocol on BNB Chain was exploited for $346,137. The attacker abused a hardcoded owner backdoor in the verified Staking contract (0x404404a845fff0201f3a4d419b4839fc419c99f7). Using a type-0x4 transaction with authorizationList, they took ownership, minted fake staking claims, redeemed ~296.5K USDT, swept SQi tokens, and dumped them in the SQi/USDT pool for additional profit. Total realized loss: approximately $346.1K.

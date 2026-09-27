# [M] Dream Health Chain incident: Dream Health Chain’s staking/reward contracts on BSC were exploited for about 71,851 USDT. A broken award state machine allowed a

## Summary
Severity: Medium
Target: Dream Health Chain
Loss: $ 71,851
Attack method: Smart Contract Vulnerability
Published: 2026-09-05
Source: https://x.com/SlowMist_Team/status/2096152539767120259
Type: slowmist-incident

## Details
Dream Health Chain’s staking/reward contracts on BSC were exploited for about 71,851 USDT. A broken award state machine allowed a claimed reward to be reset with a tiny or zero-effective DHC deposit, so the same fixed payout could be claimed repeatedly from the shared pool. The attacker looped pledge and claim, then sold about 542,070 DHC into the DHC-USDT pool.

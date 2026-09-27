# [M] Joe Agent incident: The Joe Agent ($JOE) project smart contract had a single-function reentrancy vulnerability. The attacker exploited the logic in _r

## Summary
Severity: Medium
Target: Joe Agent
Loss: $ 45,000
Attack method: Reentrancy Attack
Published: 2026-05-28
Source: https://x.com/SlowMist_Team/status/2059887450663551352
Type: slowmist-incident

## Details
The Joe Agent ($JOE) project smart contract had a single-function reentrancy vulnerability. The attacker exploited the logic in _removeLiquidityViaContract where BNB was sent via low-level call before updating lpInfo[user].lpAmount, performing ~25 reentrancy loops to steal 62.5 BNB and ~1.196M JOE.

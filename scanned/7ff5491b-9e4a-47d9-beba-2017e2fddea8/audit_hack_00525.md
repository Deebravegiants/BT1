# [M] Veil Cash incident: Veil.Cash (a zk-SNARK privacy protocol on Base, forked from Tornado Cash) suffered an exploit on its legacy fixed-denomination pri

## Summary
Severity: Medium
Target: Veil Cash
Loss: $ 5,000
Attack method: Smart Contract Vulnerability
Published: 2026-02-20
Source: https://x.com/Veildotcash/status/2025293773891404225
Type: slowmist-incident

## Details
Veil.Cash (a zk-SNARK privacy protocol on Base, forked from Tornado Cash) suffered an exploit on its legacy fixed-denomination privacy pools. Due to a misconfigured Groth16 zk-SNARK verifier (where delta2 equaled gamma2), an attacker was able to forge valid zero-knowledge proofs and drain approximately 2.9 ETH (~$5,000) in a single transaction by making multiple fraudulent withdrawals without corresponding deposits. Whitehat interveners and the exploiter voluntarily returned the funds, resulting in 100% recovery. The project’s newer/live pools were unaffected.

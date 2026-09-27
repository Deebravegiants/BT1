# [M] Wiener DOGE incident: The Wiener DOGE project was exploited maliciously, causing $30,000 in damages. Attackers exploited the inconsistency between WDODG

## Summary
Severity: Medium
Target: Wiener DOGE
Loss: $ 30,000
Attack method: Flash loan attack
Published: 2022-04-24
Source: https://mp.weixin.qq.com/s/l6XES9gtYlclw59AF1whdg
Type: slowmist-incident

## Details
The Wiener DOGE project was exploited maliciously, causing $30,000 in damages. Attackers exploited the inconsistency between WDODGE's charging mechanism and swap pools to launch the attack. The root cause of the incident is that the sender's LP pair is not excluded from the transfer fee through the tightened token contract. As a result, the attacker is able to drain the deflationary tokens in the LP pair, which in turn causes the pair price to become unbalanced.

# [M] Quint incident: Metaverse project Quint was hacked and lost $130,000. The root cause of the attack is that when the reStake function executes the

## Summary
Severity: Medium
Target: Quint
Loss: $ 130,000
Attack method: Contract Vulnerability
Published: 2022-06-30
Source: https://twitter.com/BeosinAlert/status/1542493260114931712
Type: slowmist-incident

## Details
Metaverse project Quint was hacked and lost $130,000. The root cause of the attack is that when the reStake function executes the reStake reward reStake, the reward amount of the LP token is not updated, so that the attacker can claim the issued reward multiple times.

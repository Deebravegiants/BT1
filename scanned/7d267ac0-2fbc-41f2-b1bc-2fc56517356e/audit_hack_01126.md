# [M] Poolz Finance incident: Poolz Finance's LockedDeal contract was hacked and lost about $500,000. The attacker called the vulnerable function CreateMassPool

## Summary
Severity: Medium
Target: Poolz Finance
Loss: $ 500,000
Attack method: Contract Vulnerability
Published: 2023-03-15
Source: https://twitter.com/Poolz__/status/1635899850918178817
Type: slowmist-incident

## Details
Poolz Finance's LockedDeal contract was hacked and lost about $500,000. The attacker called the vulnerable function CreateMassPools in the LockedDeal contract, and triggered an integer overflow vulnerability in the parameter _StartAmount. In addition to obtaining a large number of poolz tokens, the attacker also obtained other tokens.

# [H] zkLend incident: The leading lending platform on the Starknet chain, zkLend, has suffered an attack. The core reason for this breach lies in the fa

## Summary
Severity: High
Target: zkLend
Loss: $ 9,600,000
Attack method: Contract Vulnerability
Published: 2025-02-12
Source: https://x.com/SlowMist_Team/status/1890351732313714882
Type: slowmist-incident

## Details
The leading lending platform on the Starknet chain, zkLend, has suffered an attack. The core reason for this breach lies in the fact that the value of the accumulator in an empty market can be manipulated and amplified using a unique mechanism in flash loans. Additionally, the market contract's use of the SafeMath library performs division using direct division, allowing the attacker to exploit the amplified accumulator to trigger a rounding-down vulnerability for profit.

# [M] SIR.trading incident: According to the SlowMist MistEye security monitoring system, the leveraged trading project SIR.trading (@leveragesir) on the Ethe

## Summary
Severity: Medium
Target: SIR.trading
Loss: $ 355,000
Attack method: Contract Vulnerability
Published: 2025-03-30
Source: https://x.com/SlowMist_Team/status/1906722264059674893
Type: slowmist-incident

## Details
According to the SlowMist MistEye security monitoring system, the leveraged trading project SIR.trading (@leveragesir) on the Ethereum chain has been attacked, resulting in a loss of over $300,000 in assets. The root cause of this hack is that the transiently stored value set using tstore in the function was not cleared after the function call ended. This allowed the attacker to exploit this characteristic by constructing specific malicious addresses to bypass permission checks and transfer tokens.

# [M] BYToken incident: The public triggerAutoBurn() maintenance function in BYToken contract on BSC was abused. The attacker took a Moolah flashloan (~42

## Summary
Severity: Medium
Target: BYToken
Loss: $ 87,402
Attack method: Smart Contract Vulnerability
Published: 2026-06-04
Source: https://x.com/TenArmorAlert/status/2062708160700322257
Type: slowmist-incident

## Details
The public triggerAutoBurn() maintenance function in BYToken contract on BSC was abused. The attacker took a Moolah flashloan (~422k WBNB), performed Pancake swaps, then called the unprivileged function. This burned ~67.8 quadrillion BY directly from the BY/WBNB pair and called pair.sync(), rewriting reserves to 1 BY + full WBNB. The extreme skew allowed massive BY sells to drain nearly all WBNB liquidity, netting the attacker ~146.60 BNB ($87,402).

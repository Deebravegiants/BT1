# [M] ONTR incident: The ONTR token project was drained due to a flawed onlyOwner check in the contract (accepts owner == address(0)). This allowed re-

## Summary
Severity: Medium
Target: ONTR
Loss: $ 98,200
Attack method: Smart Contract Vulnerability
Published: 2026-05-28
Source: https://x.com/TenArmorAlert/status/2060190914547449936
Type: slowmist-incident

## Details
The ONTR token project was drained due to a flawed onlyOwner check in the contract (accepts owner == address(0)). This allowed re-owning a renounced token. The attacker used hidden balance-grant logic to fake massive ONTR balances (no totalSupply/mint logs), dumped into the ONTR/WETH LP, and swapped out WETH for profit.

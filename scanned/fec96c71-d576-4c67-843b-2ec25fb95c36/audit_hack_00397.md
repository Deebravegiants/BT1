# [M] AIDC incident: AIDC token on BSC was exploited due to a flaw in _sellTransfer()/burn logic. The attacker manipulated the PancakeSwap LP pool, cau

## Summary
Severity: Medium
Target: AIDC
Loss: $ 121,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-28
Source: https://x.com/SlowMist_Team/status/2071437371590238249
Type: slowmist-incident

## Details
AIDC token on BSC was exploited due to a flaw in _sellTransfer()/burn logic. The attacker manipulated the PancakeSwap LP pool, causing burn fees to accumulate without properly deducting from sender balance, draining ~$121K WBNB.

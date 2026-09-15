# [M] LOOPSDAO incident: LOOPSDAO’s LpdFi protocol on BSC was exploited. The attacker used a flash loan to manipulate the spot price of the thin PancakeSwa

## Summary
Severity: Medium
Target: LOOPSDAO
Loss: $ 690000
Attack method: Price Manipulation
Published: 2026-08-02
Source: https://x.com/DefimonAlerts/status/2084157533204197380
Type: slowmist-incident

## Details
LOOPSDAO’s LpdFi protocol on BSC was exploited. The attacker used a flash loan to manipulate the spot price of the thin PancakeSwap LPD/USDC pair (no TWAP or deviation guard), opened a massively inflated interest-bearing position with minimal LPD, and claimed interest right across the daily settlement boundary. This triggered the protocol to burn its own Cake-LP and pay out the inflated amount, draining approximately $690,000.

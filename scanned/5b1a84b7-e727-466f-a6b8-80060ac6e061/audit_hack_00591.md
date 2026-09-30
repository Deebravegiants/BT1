# [M] D3X AI incident: D3X AI (@D3X_AI) was attacked on BSC, resulting in a loss of approximately $158.9K.

The root cause was that the exchange() func

## Summary
Severity: Medium
Target: D3X AI
Loss: $ 158,900
Attack method: Price Manipulation
Published: 2025-08-16
Source: https://bscscan.com/tx/0x26bcefc152d8cd49f4bb13a9f8a6846be887d7075bc81fa07aa8c0019bd6591f
Type: slowmist-incident

## Details
D3X AI (@D3X_AI) was attacked on BSC, resulting in a loss of approximately $158.9K.

The root cause was that the exchange() function of contract 0xb8ad relied on the spot price of the d3xat token from a UniswapV2 pair, which the attacker exploited through a price manipulation attack.

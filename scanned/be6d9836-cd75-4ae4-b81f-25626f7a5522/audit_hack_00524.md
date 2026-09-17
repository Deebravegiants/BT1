# [C] Blend Pools V2 incident: Blend Pools V2 (specifically the YieldBlox DAO-managed lending pool on Stellar) was exploited. The attacker manipulated the price

## Summary
Severity: Critical
Target: Blend Pools V2
Loss: $ 10,200,000
Attack method: Oracle Manipulation Attack
Published: 2026-02-22
Source: https://x.com/blockaid_/status/2057118828740374669?s=46&amp;t=DLwbX9Nw4QECiyZQ0av-fg
Type: slowmist-incident

## Details
Blend Pools V2 (specifically the YieldBlox DAO-managed lending pool on Stellar) was exploited. The attacker manipulated the price of the low-liquidity asset USTRY ~100x higher in a single trade on Stellar DEX (SDEX). This manipulated the Reflector oracle price feed. The attacker then deposited the overvalued USTRY as collateral into the Blend Pools V2 lending pool and borrowed approximately $10.2M–$10.97M worth of XLM and USDC. Stellar validators and Blockaid responded quickly, freezing a large portion (~48M XLM / ~$7.3M) of the funds. Most of the stolen assets were contained, though some USDC was bridged out.

# [M] Chi Protocol incident: Chi Protocol (a DeFi stablecoin protocol issuing $USC backed by LSTs/LRTs on Ethereum) was exploited due to a logic error in the A

## Summary
Severity: Medium
Target: Chi Protocol
Loss: $ 8,500
Attack method: Smart Contract Logic Vulnerability
Published: 2026-07-13
Source: https://x.com/DefimonAlerts/status/2076887008773829119
Type: slowmist-incident

## Details
Chi Protocol (a DeFi stablecoin protocol issuing $USC backed by LSTs/LRTs on Ethereum) was exploited due to a logic error in the ArbitrageV5 contract’s burn() function. The attacker used a flash loan to buy heavily depegged $USC cheaply on a thin Uniswap V2 pool and burned it to redeem full-value collateral (weETH/stETH/WETH) at the hardcoded $1 peg, without the burn function checking the actual peg (unlike the mint function). This resulted in approximately $8,500 loss, nearly draining the protocol’s reserves.

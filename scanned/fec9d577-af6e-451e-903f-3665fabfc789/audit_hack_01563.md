# [M] SushiSwap incident: The liquidity mining project SushiSwap (SUSHI) community governor 0xMaki announced in the Discord group that the SushiSwap vulnera

## Summary
Severity: Medium
Target: SushiSwap
Loss: $ 15,000
Attack method: Price Manipulation
Published: 2020-11-30
Source: https://www.btcfans.com/en-us/flash/id-43549
Type: slowmist-incident

## Details
The liquidity mining project SushiSwap (SUSHI) community governor 0xMaki announced in the Discord group that the SushiSwap vulnerability has been fixed, and the lost funds (approximately US$10,000) will be compensated from the SUSHI asset library. Previously, SushiSwap was attacked by a liquidity provider. The attacker obtained between 10,000 and 15,000 US dollars in a transaction. However, after this operation was discovered by 0xMaki, 0xMaki sent a transaction to the attacker with a message saying "I found you and we are working hard to fix it. Contact me on Discord to get bug bounty-0xMaki". According to analysis, the attacker uses SLP and WETH to create a new token pool, uses SLP1 of the new token pool to convert in Sushi Maker, and uses a small amount of SLP to transfer all SLPs in the Sushi Maker contract to the tokens they created. In the pool, all the handling fees of the corresponding transaction pair within a period of time will be collected into the bag. Repeat this process for other trading pairs and continue to make profits.

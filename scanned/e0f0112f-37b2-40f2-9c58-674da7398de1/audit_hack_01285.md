# [M] bDollar incident: The first algorithmic stablecoin project on Binance Smart Chain, bDollar, suffered a price manipulation attack, and the attacker m

## Summary
Severity: Medium
Target: bDollar
Loss: 2381 WBNB
Attack method: Price Manipulation
Published: 2022-05-21
Source: https://www.defidaonews.com/article/6752278
Type: slowmist-incident

## Details
The first algorithmic stablecoin project on Binance Smart Chain, bDollar, suffered a price manipulation attack, and the attacker made a profit of 2,381 WBNB (worth about $730,000). This attack mainly exploits the design loophole of the claimAndReinvestFromPancakePool function in the DAO fund proxy contract CommunityFund when adding liquidity. It does not fully consider that after the price is maliciously raised, the project party will passively use the funds in its own contract when adding liquidity. The situation of high-level connection.

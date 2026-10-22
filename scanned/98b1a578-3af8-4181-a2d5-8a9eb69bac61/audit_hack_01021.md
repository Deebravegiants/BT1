# [M] LeetSwap incident: The axlUSD/WETH pool in LeetSwap, the largest DEX on the Base chain, suffered a price manipulation attack and has suspended tradin

## Summary
Severity: Medium
Target: LeetSwap
Loss: $ 624,000
Attack method: Price Manipulation
Published: 2023-08-01
Source: https://twitter.com/LeetSwap/status/1686190488506769408
Type: slowmist-incident

## Details
The axlUSD/WETH pool in LeetSwap, the largest DEX on the Base chain, suffered a price manipulation attack and has suspended trading for investigation. It appears that 342.5 ETH (~$624,000) was exploited. On August 3, LeetSwap stated that it had withdrawn about 400 ETH from the risky liquidity pool. According to the analysis of SlowMist, the main cause of this attack was that the _transferFeesSupportingTaxTokens function in the Pair contract was externally callable. This function allowed the transfer of any specified tokens in the contract to the address that collects fees. The attacker initiated a normal small-swap operation first to acquire the necessary tokens for the next swap. Then, the attacker called the _transferFeesSupportingTaxTokens function to transfer almost all of the tokens of one of the Pair to the address collecting fees, causing an imbalance in the Pair's liquidity. Finally, the attacker called the sync function to balance the pool and performed a reverse swap to take more ETH than expected.

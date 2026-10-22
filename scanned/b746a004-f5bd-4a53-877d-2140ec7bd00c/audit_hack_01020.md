# [M] Uwerx network incident: he Uwerx network was attacked and lost about 174.78 ETH. According to the analysis of SlowMist, the root cause is that when the re

## Summary
Severity: Medium
Target: Uwerx network
Loss: $ 324,000
Attack method: Price Manipulation
Published: 2023-08-02
Source: https://twitter.com/SlowMist_Team/status/1686674169189249024
Type: slowmist-incident

## Details
he Uwerx network was attacked and lost about 174.78 ETH. According to the analysis of SlowMist, the root cause is that when the receiving address is uniswapPoolAddress (0x01), it will burn off 1% more tokens of the transfer amount of the from address, so the attacker uses the skim function of the uniswapv2 pool to consume a large number of WERX tokens, and then calls the sync function to maliciously inflate the price of the token, and then reverses the swap to extract the ETH to gain profit.

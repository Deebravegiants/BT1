# [M] SushiSwap incident: SushiSwap's BentoBoxv1 contract was attacked, and the hacker made a profit of about $26,000. According to analysis, the attack is

## Summary
Severity: Medium
Target: SushiSwap
Loss: $ 26,000
Attack method: Price Manipulation
Published: 2023-02-10
Source: https://www.panewslab.com/zh/sqarticledetails/dw2h404u.html
Type: slowmist-incident

## Details
SushiSwap's BentoBoxv1 contract was attacked, and the hacker made a profit of about $26,000. According to analysis, the attack is due to the Kashi Medium Risk ChainLink price update later than the mortgage/loan. In the two attack transactions, the attacker flashloaned 574,275 and 785,560 xSUSHI respectively. After mortgage and loan, the price of kmxSUSHI/USDT in LINK Oracle dropped by 16.9%. By exploiting this price gap, the attacker can call the liquidate() function to liquidate and obtain 15,429 and 11,333 USDT.

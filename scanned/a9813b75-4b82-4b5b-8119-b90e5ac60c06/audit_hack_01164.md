# [H] LendHub incident: According to SlowMist, LendHub, the HECO ecological cross-chain lending platform, was suspected of being attacked and lost nearly

## Summary
Severity: High
Target: LendHub
Loss: $ 6,000,000
Attack method: Contract Vulnerability
Published: 2023-01-13
Source: https://www.panewslab.com/zh/sqarticledetails/obl5l5ms.html
Type: slowmist-incident

## Details
According to SlowMist, LendHub, the HECO ecological cross-chain lending platform, was suspected of being attacked and lost nearly 6 million US dollars. The main hacker profit address is 0x9d01..ab03. The reason for this attack is that there are two lBSV cTokens in LendHub, one of which has been abandoned in April 2021 but has not been removed from the market, which resulted in both the old and new lBSV existing in the market. Moreover, the Comptrollers corresponding to the old and new lBSV are not the same, but both have prices in the market, which results in a split in the calculation of liabilities in the old and new markets. Attackers take advantage of this problem to redeem mortgages in the old market and carry out lending operations in the new market, maliciously extorting protocol funds in the new market. At present, the main profit address for hackers is 0x9d01..ab03, and the source of the hacker attack fee is the 100 ETH received from Tornado.Cash on January 12. SlowMist said that through the threat intelligence network, some traces of hackers have been obtained.

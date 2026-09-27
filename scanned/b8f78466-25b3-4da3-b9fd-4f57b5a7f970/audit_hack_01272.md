# [M] treasure swap incident: The treasure swap project was attacked. The attacker only used 0.000000000000000001 WETH to exchange all the WETH tokens in the tr

## Summary
Severity: Medium
Target: treasure swap
Loss: 3,945 BNB
Attack method: K-value Verification Vulnerability
Published: 2022-06-11
Source: https://www.panewslab.com/zh/sqarticledetails/91mr6yag.html
Type: slowmist-incident

## Details
The treasure swap project was attacked. The attacker only used 0.000000000000000001 WETH to exchange all the WETH tokens in the transaction pool. The reverse of the source code found that the swap function of the attacked contract lacked the K value check. At present, the attacker has completed the attack on the two contracts 0xe26e436084348edc0d5c7244903dd2cd2c560f88 and 0x96f6eb307dcb0225474adf7ed3af58d079a65ec9, and accumulated a profit of 3,945 BNB.

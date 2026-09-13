# [M] Thoreum Finance incident: Thoreum Finance was hacked. According to analysis, because the transfer function of the non-open source contract 0x79fe created by

## Summary
Severity: Medium
Target: Thoreum Finance
Loss: $ 580,000
Attack method: Contract Vulnerability
Published: 2023-01-19
Source: https://www.panewslab.com/zh/sqarticledetails/chr92pfw.html
Type: slowmist-incident

## Details
Thoreum Finance was hacked. According to analysis, because the transfer function of the non-open source contract 0x79fe created by the Thoreum Finance project party is suspected to have a loophole, when the from and to addresses of the transfer function are the same, due to the use of temporary variables to store the balance, the balance will double when you transfer to yourself , the attacker repeated the operation many times, and finally made a profit of 2,000 BNB, involving an amount of about 580,000 US dollars.

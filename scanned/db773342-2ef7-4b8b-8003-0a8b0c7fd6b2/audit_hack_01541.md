# [C] Alpha Finance/Cream Finance incident: The attacker uses Lightning Loan to Alpha Finance for leveraged lending, and uses Alpha Finance’s own Cream IronBank quota to retu

## Summary
Severity: Critical
Target: Alpha Finance/Cream Finance
Loss: $ 37,500,000
Attack method: Flash loan attack
Published: 2021-02-13
Source: https://medium.com/cream-finance/alpha-homora-v2-exploit-post-mortem-344d277bdea6
Type: slowmist-incident

## Details
The attacker uses Lightning Loan to Alpha Finance for leveraged lending, and uses Alpha Finance’s own Cream IronBank quota to return the Lightning Loan. In this process, the attacker obtains a large amount of cySUSD by adding liquidity to Cream, allowing the attacker to use it. These cySUSD are further borrowed in Cream Finance. Due to problems with Alpha Finance, both agreements suffered losses at the same time.

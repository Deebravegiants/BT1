# [C] Penpie incident: The decentralized liquidity yield project Penpie was attacked, resulting in nearly $30 million in losses. According to the analysi

## Summary
Severity: Critical
Target: Penpie
Loss: $ 27,348,259
Attack method: Contract Vulnerability
Published: 2024-09-04
Source: https://www.odaily.news/newsflash/388884
Type: slowmist-incident

## Details
The decentralized liquidity yield project Penpie was attacked, resulting in nearly $30 million in losses. According to the analysis by the SlowMist security team, the core issue of this incident lies in Penpie’s erroneous assumption that all markets created by Pendle Finance are legitimate when registering new Pendle markets. However, Pendle Finance’s market creation process is open, allowing anyone to create a market with customizable key parameters such as the SY contract address. Exploiting this, the attacker created a market contract with a malicious SY contract. They leveraged Penpie’s mechanism, which required calls to external SY contracts to claim rewards, and used flash loans to inject a large amount of liquidity into the market and pool, artificially inflating the rewards and profiting from it.

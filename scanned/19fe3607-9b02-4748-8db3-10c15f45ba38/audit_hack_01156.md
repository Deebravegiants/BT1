# [C] BonqDAO & AllianceBlock incident: Non-custodial lending platform BonqDAO and crypto infrastructure platform AllianceBlock were hacked due to a bug in BonqDAO's smar

## Summary
Severity: Critical
Target: BonqDAO & AllianceBlock
Loss: $ 120,000,000
Attack method: Price Manipulation
Published: 2023-02-02
Source: https://www.theblock.co/post/207799/bonqdao-exploited-for-88-million-allianceblock-tokens-stolen-during-the-exploit
Type: slowmist-incident

## Details
Non-custodial lending platform BonqDAO and crypto infrastructure platform AllianceBlock were hacked due to a bug in BonqDAO's smart contracts, resulting in losses of approximately $120 million. Among them, hackers removed approximately 114 million WALBT ($11 million), AllianceBlock’s wrapped native token, and 98 million BEUR tokens ($108 million) from a BonqDAO vault. According to the analysis of SlowMist, the root cause of the attack is that the attacker uses the oracle machine to quote the required collateral, which is much lower than the profit obtained by the attack, thereby manipulating the market and liquidating other users by maliciously submitting wrong prices. In addition, AllianceBlock stated that the incident has nothing to do with the BonqDAO vault, no smart contracts were breached, and both teams are working on eliminating liquidity to mitigate hackers converting stolen tokens into other assets.

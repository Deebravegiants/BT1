# [H] Optimism incident: Optimism and Wintermute both released announcements, disclosing to the community a loss of 20 million OP tokens. At the time of th

## Summary
Severity: High
Target: Optimism
Loss: 2,000,000 OP
Attack method: Multi-signature address transfer vulnerability
Published: 2022-06-09
Source: https://twitter.com/optimismPBC/status/1534631766576836608
Type: slowmist-incident

## Details
Optimism and Wintermute both released announcements, disclosing to the community a loss of 20 million OP tokens. At the time of the release of OP tokens, Optimism entrusted Wintermute to provide liquidity services for OP in the secondary market. As part of the agreement, Optimism will provide Wintermute with 20 million OP tokens. To receive the tokens, Wintermute gave Optimism a multi-signature address, to which Optimism transferred 20 million OPs after Optimism test sent two transactions and Wintermute confirmed it was correct. After Optimism transferred the coins, Wintermute found that they had no way to control these coins, because the multi-signature addresses they provided were only deployed on the Ethereum mainnet for the time being and have not yet been deployed to the Optimism network. To gain control of these tokens, Wintermute immediately initiated remediation operations. However, attackers have already noticed this vulnerability and deployed multi-signature to this address on the Optimism network before Wintermute, successfully controlling the 20 million tokens. At present, the Optimism hacker has returned 17 million OP tokens and transferred 1 million OP to the Vitalik address, and Vitalik has returned the funds.

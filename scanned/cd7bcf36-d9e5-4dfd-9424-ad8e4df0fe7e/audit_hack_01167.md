# [M] BRA incident: The price of BRA token on BNB Chain is zero. According to the analysis, the token will be taxed during the transaction, and the ta

## Summary
Severity: Medium
Target: BRA
Loss: 820 WBNB
Attack method: Taxation Mechanism Flaw
Published: 2023-01-10
Source: https://www.panewslab.com/zh/sqarticledetails/ql0656re.html
Type: slowmist-incident

## Details
The price of BRA token on BNB Chain is zero. According to the analysis, the token will be taxed during the transaction, and the tax collected will be directly sent to the transaction pair, and the tax will be added twice. Under this mechanism, after many such transactions, the number of tokens in the transaction pair continues to increase. At the same time, any user can call the skim function to retrieve the extra tokens in the transaction pair, which results in the actual number of tokens exceeding its issuance limit. This BRA token attack has caused 820 WBNB losses. The address of the attacker (0xE2Ba15be8C6Fb0d7C1F7bEA9106eb8232248FB8B).

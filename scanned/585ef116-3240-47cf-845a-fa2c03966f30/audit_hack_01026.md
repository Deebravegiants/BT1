# [M] Carson incident: The BSC ecology Carson was attacked and lost about $145,000. At present, the price of Carson tokens has dropped by 96%, and the at

## Summary
Severity: Medium
Target: Carson
Loss: $ 145,000
Attack method: Flash Loan Attack
Published: 2023-07-27
Source: https://twitter.com/BeosinAlert/status/1684393202252402688?s=20
Type: slowmist-incident

## Details
The BSC ecology Carson was attacked and lost about $145,000. At present, the price of Carson tokens has dropped by 96%, and the attacker has exchanged the stolen assets for 600 BNB and transferred them to Tornado Cash. The attacker repeatedly called the swapExactTokensForTokensSupportingFeeOnTransferTokens function in the 0x2bdf...341a contract (not open-source) through flash loans, swapped for BUSD and burned Carson in the pair, then repeatedly inflated the price of Carson for profit.

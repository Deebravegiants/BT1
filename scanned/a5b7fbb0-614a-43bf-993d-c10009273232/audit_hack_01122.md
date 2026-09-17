# [M] Indexed Finance incident: Indexed Finance's ORCL5 Token contract was attacked by a flash loan and lost $9,925. Root cause preliminary analysis is that "calc

## Summary
Severity: Medium
Target: Indexed Finance
Loss: $ 9,925
Attack method: Flash Loan Attack
Published: 2023-03-21
Source: https://twitter.com/AnciliaInc/status/1637925297327865856
Type: slowmist-incident

## Details
Indexed Finance's ORCL5 Token contract was attacked by a flash loan and lost $9,925. Root cause preliminary analysis is that "calcSingleOutGivenPoolIn()" calculates wrong value of tokenAmountOut.

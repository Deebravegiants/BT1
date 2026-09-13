# [H] Platypus incident: The stablecoin trading project Platypus encountered a flash loan attack on AAVE, resulting in a total asset loss of approximately

## Summary
Severity: High
Target: Platypus
Loss: $ 9,000,000
Attack method: Flash Loan Attack
Published: 2023-02-17
Source: https://twitter.com/Platypusdefi/status/1626396538611310592
Type: slowmist-incident

## Details
The stablecoin trading project Platypus encountered a flash loan attack on AAVE, resulting in a total asset loss of approximately $9 million. According to the analysis, the vulnerability seems to lie in the verification of the MasterPlatypusV4 contract by the emergencyWithdraw function, which will only fail when the borrowed assets exceed the borrowing limit. The function then proceeds to transfer all of the user's deposit assets regardless of the value of the user's borrowed assets. On Feb. 18, The Block reported that at least $2.4 million has been recovered with the help of security firms after the Platypus hack.

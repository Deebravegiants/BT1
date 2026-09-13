# [M] OWNLY incident: The ownlyio project's NFTStaking contract was attacked, with a total of 115 BNB stolen and a loss of about $36,418. The reason for

## Summary
Severity: Medium
Target: OWNLY
Loss: 115 BNB
Attack method: Contract Vulnerability
Published: 2022-05-10
Source: https://twitter.com/ownlyio/status/1524149988837580800
Type: slowmist-incident

## Details
The ownlyio project's NFTStaking contract was attacked, with a total of 115 BNB stolen and a loss of about $36,418. The reason for this attack is that the unstake function of the pledge contract of the ownio project does not check the user's claim status, so the attacker can use the unstake function to receive the own tokens in the contract infinitely, thereby extracting all the own tokens in the pledge contract, and finally the attacker The acquired owned tokens are exchanged for 115 BNB through the pair transaction.

# [M] BEVO incident: The BEVO NFT Art Token (BEVO) on BSC was exploited with a total loss of approximately $45,000. The root cause is that BEVO is a de

## Summary
Severity: Medium
Target: BEVO
Loss: $ 45,000
Attack method: Reward Mechanism Flaw
Published: 2023-01-30
Source: https://twitter.com/BlockSecTeam/status/1620030206571593731
Type: slowmist-incident

## Details
The BEVO NFT Art Token (BEVO) on BSC was exploited with a total loss of approximately $45,000. The root cause is that BEVO is a deflationary token, and the attacker calls the function deliver(), the value of _rTotal will decrease, which will further affect the return value of getRate() used to calculate the balance. After the attacker manipulates the token balance, he calls the function skim to transfer the increased PancakePair balance to his own account. Finally, the attacker calls the function deliver() again and exchanges the increased BEVO back to WBNB.

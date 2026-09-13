# [M] Xave Finance incident: The Xave Finance project was hacked, resulting in a 1000x increase in RNBW issuance. The attack transaction is 0xc18ec2eb7d41638d9

## Summary
Severity: Medium
Target: Xave Finance
Loss: $ 635
Attack method: Contract Vulnerability
Published: 2022-10-09
Source: https://mobile.twitter.com/AnciliaInc/status/1578952542926491650
Type: slowmist-incident

## Details
The Xave Finance project was hacked, resulting in a 1000x increase in RNBW issuance. The attack transaction is 0xc18ec2eb7d41638d9982281e766945d0428aaeda6211b4ccb6626ea7cff31f4a. The attacker first creates the attack contract 0xe167cdaac8718b90c03cf2cb75dc976e24ee86d3. The attack contract first calls the executeProposalWithIndex() function of the DaoModule contract 0x8f90 to execute the proposal. The content of the proposal is to call the mint() function to mint 100,000,000,000,000 RNBWs and transfer the ownership rights to the attacker. Finally, the hacker exchanged it for xRNBW, which was stored at the attacker's address (0x0f44f3489D17e42ab13A6beb76E57813081fc1E2).

# [M] Solend incident: Solana Ecological Lending Agreement Solend tweeted that the agreement was hacked at 20:40 on August 19th, Beijing time. The attack

## Summary
Severity: Medium
Target: Solend
Loss: $ 16,000
Attack method: Contract Vulnerability
Published: 2021-08-19
Source: https://twitter.com/solendprotocol/status/1428611597941891082
Type: slowmist-incident

## Details
Solana Ecological Lending Agreement Solend tweeted that the agreement was hacked at 20:40 on August 19th, Beijing time. The attacker cracked the insecure identity check in the UpdateReserveConfig function, allowing it to liquidate all accounts. In addition, the hacker also set the APY of borrowed funds to 250%. During this period, the funds of 5 users were mistakenly liquidated, and the liquidator is currently refunding the losses of these 5 users totaling USD 16,000. Solend said that this attack did not result in the theft of funds, and that the scale of the bug bounty will be increased and a better monitoring and alarm system will be established.

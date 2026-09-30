# [H] Deus DAO exploit: An unexpected plot twist saw Deus DAO users liquidated via a flash loan attack on the recently launched DEI lending contract , with the attacker makin

## Summary
Severity: High
Target: Deus DAO
Loss: $3,000,000
Published: 03/15/2021
Source: https://rekt.news/deus-dao-rekt
Type: rekt-postmortem

## Details
## Deus DAO - REKT

 Tuesday, March 15, 2022 Deus DAO - Fantom - REKT 

 read this article also in : zh 

 Deus rekt machina. 

 An unexpected plot twist saw Deus DAO users liquidated via a flash loan attack on the recently launched DEI lending contract , with the attacker making ~$3M profit.

 Five months have passed since we last reported a flash loan attack, but they used to be commonplace.

 Is DeFi growing stronger? 

 A flash loan attack was used to manipulate the balance of the Solidex USDC/DEI pool, which is used as an oracle for collateral value on Deus Finance’s $DEI lending contract. 

 This resulted in user positions becoming insolvent, which the hacker’s contract liquidated, before repaying the flash loan.

 Credit: Peckshield 

 1: Flashloan 9,739342 DEI via SPIRIT-LP_USDC_DEI

 2: Flashloan 24,772,798 DEI out of the sAMM-USDC/DEI pair (used as price oracle to calculate collateral value)

 3: Liquidate the users who become insolvent from Step 2

 4: Repay the borrowed 24,772,798 DEI to the sAMM-USDC/DEI pair

 5: Burn the liquidated LP token to get 5,218,173 USDC + 5,246,603 DEI

 6: Swap 5,218,173 USDC to 5,170,594 DEI

 7: Repay flashloan with 3,001,552 DEI as hack profit

 Attack tx: 

 0xe374495036fac18aa5b1a497a17e70f256c4d3d416dd1408c026f3f5c70a3a9c 

 The attacker then went on to send 3M USDC via Multichain from an FTM address to ETH address , and from there 1.1k ETH and 200k DAI to Tornado cash, totalling ~$3M gained. 

 The project’s token, DEUS , dropped ~40% in the hour following the attack and, despite some recovery, remains volatile.

 Deus have announced that they will be reimbursing affected users who return their DEI debts, returning their liquidated collateral.

 Flash loan season taught even non-technical users about the importance of price oracles. 

 Security standards emerged from our baptism of fire, and the industry learned and moved forward.

 We know that these attacks can be mitigated by using decentralised or TWAP oracles. 

 Why didn’t Deus DAO have a more robust system in place? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

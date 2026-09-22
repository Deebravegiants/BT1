# [C] Hedgey Finance exploit: Hedgey Finance rocked by $44.7 million flash loan attack across both the Arbitrum and Ethereum platforms

## Summary
Severity: Critical
Target: Hedgey Finance
Loss: $44,700,000
Published: 04/19/2024
Source: https://rekt.news/hedgey-finance-rekt
Type: rekt-postmortem

## Details
## Hedgey Finance - Rekt

 Friday, April 19, 2024 Hedgey Finance - REKT 

 read this article also in : zh 

 Not a good strategy to hedge your bets. 

 Hedgey Finance rocked by $44.7 million flash loan attack across both the Arbitrum and Ethereum platforms. 

 The exploit was first reported by Cyvers and confirmed by the Hedgey team just a little over a couple of hours later.

 Hedgey informed the community that they were investigating an attack on the Hedgey Token Claim Contract. Urging users who have created active claims, to please cancel them using the " End Token Claim " button to mitigate further losses. 

 Touted by Hedgey as “The #1 token vesting and lockup tools.” The platform provides token infrastructure for onchain teams.

 It appears the lockup tools were not secure enough, as the thieves drained just over $2.1m worth of assets from the Ethereum contract, consisting of USDC , NOBL , and MASA tokens.

 On the Arbitrum chain, the attacker was able to steal roughly $42.6m worth of BONUS tokens.

 NobleBlocks(NOBL) gave a detailed security report to their community. Bonus Block(BONUS) briefly posted “Our vestings are safe" and MASA seemed more concerned with hosting Twitter Spaces than informing their community about the exploit. 

 As the dust settles, the big question remains, how did Hedgey's vaunted security fail so catastrophically? 

 Credit: Cyvers , Hedgey Finance , NobleBlocks , Blocksec 

 On April 19, Hedgey Finance was exploited across a series of transactions, which resulted in a loss of $2.1 million on the Ethereum Mainnet and $42.6 million worth of assets on the Arbitrum network, totaling approximately $44.7 million. 

 The root cause of the exploit is the lack of input validation on users' parameters, which allowed the attacker to manipulate and gain unauthorized token approvals.

 The attacker took a flash loan of $1.3 million USDC from Balancer to abuse and manipulate the 
```
claimLockup
```
 parameter within the 
```
createLockedCampaign
```
 function of the exploited contract to trick this vulnerable contract into approving USDC token transfer to the attack contract.

 In the second step, the attacker used the approval to transfer USDC to themselves.

 Executing in two separate transactions, likely to prevent being front-run by bots.

 After checking the commit records of the vulnerable contract, the root cause was confirmed to be Unverified User Input; there was less verification of the parameters passed by users, resulting in tokens being approved to the attacker's contract.

 Exploiter’s address on Ethereum:
 https://etherscan.io/address/0xded2b1a426e1b7d415a40bcad44e98f47181dda2 

 Attack Contract on Ethereum:
 https://etherscan.io/address/0xc793113f1548b97e37c409f39244ee44241bf2b3 

 Exploited Contract on Ethereum:
 https://etherscan.io/address/0xbc452fdc8f851d7c5b72e1fe74dfb63bb793d511 

 Exploiter’s address on Arbitrum:

 https://arbiscan.io/txs?a=0xc7241e27ee4b8d32b59a10e848b48530047a8c5b 

 Attack Contract on Arbitrum:

 https://arbiscan.io/txs?a=0xbb52f1723ddf2c84ba2668f4e04712f572cbf780 

 Exploited Contract on Arbitrum:
 https://arbiscan.io/address/0xbc452fdc8f851d7c5b72e1fe74dfb63bb793d511 

 Funds are currently being held here .

 Hedgey sent an onchain message to the attacker looking to get in touch and discuss next steps. They’re assuming it is a white hat and even told them “well done” for finding the exploit. 

 Thanks for robbing us, you’re one of the good guys, right? 

 Consensys Diligence audited Hedgey’s Token Lockup and Vesting Plans in June and July of 2023.

 Whether it was a white hat or a black hat, doesn’t matter, someone still made away with $44.7 million. 

 Isn’t calling theft "well done" an insult to every user whose funds were compromised? 

 While Hedgey praises the attacker's skills and holds out hope they are a white hat actor, the nearly $45 million reality check exposes alarming gaps in their security practices. 

 Hedgey Finance faces an uphill battle to rebuild trust, beginning with a comprehensive security overhaul.

 It may be a good idea to execute a complete security revamp, fortifying input validation, reinforcing access controls, and enduring stringent audits to prevent history from repeating itself. 

 With millions of dollars lost and trust shaken, the path to recovery will be a long and challenging one.

 By scrutinizing its security practices and learning from these costly mistakes, Hedgey can begin the arduous journey towards rebuilding its reputation and restoring faith within the decentralized finance community. 

 The decentralized finance landscape is a breeding ground for innovation but also presents a constant reminder that the stakes are high, and the consequences of negligence can be dire.

 For Hedgey, this exploit serves as a cautionary tale and a reminder that security must always be the top priority. 

 The question remains: can Hedgey redeem itself and regain the trust of its users or will this event forever taint its standing in the world of DeFi? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

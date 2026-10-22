# [H] THORChain exploit: Even the old gods cannot escape the exploits

## Summary
Severity: High
Target: THORChain
Loss: $5,000,000
Published: 07/15/2021
Source: https://rekt.news/thorchain-rekt
Type: rekt-postmortem

## Details
## THORChain - REKT

 Friday, July 16, 2021 THORChain - REKT 

 read this article also in : zh 

 Even the old gods cannot escape the exploits. 
 As the cross-chain attacks continue, THORChain becomes the latest victim.

 $5 million taken in various assets from the recently updated THORChain Bifrost bridge code. 

 Cronje wrote that innovation leads to exploitation , but as attacks are so common, it seems that so does replication , or even slight alteration .

 The number of names listed on our leaderboard is steadily rising, and these are not all fast forks or cheap copy-paste protocols.

 THORChain has a dedicated user base, and their peak market cap reached nearly $5 billion just two months ago (now at $1.2B).

 How can such an established platform still fall victim to an anonymous attacker? 

 Attacker Wallet: 0x3a196410a0f5facd08fd7880a4b8551cd085c031 

 Contract Address: 0x4a33862042d004d3fc45e284e1aafa05b48e3c9c 

 Tornado Address: 0x4b713980d60b4994e0aa298a66805ec0d35ebc5a 

 According to ThorChain’s preliminary incident report , the bug was located within the ETH Bifrost (bridge) code .

 The code contains an over-ride loop, designed only for use in vaultTransferEvent transactions, which the hacker was able to manipulate. The hacker was able to wrap the router with their own contract , allowing them to access this over-ride.

 A transaction was sent with call value of 0 and deposit amount of 0. However, the over-ride loop caused the transaction’s msg.value, set at 200, to be mistakenly read as the txvalue().

 The exploit was then used in a loop, draining liquidity in various coins: 

- 2,500 ETH

- 57,975.33 SUSHI

- 8.7365 YFI

- 171,912.96 DODO

- 514.519 ALCX

- 1,167,216.739 KYL

- 13.30 AAVE

 Although the code contains a comment that explicitly states... 

 ”// it is important to keep this part outside the above loop”

 … the vulnerability was left open, and looks to have been a costly oversight for the ThorChain team.

 According to the incident report:

 ”The fix is to make the over-ride only happen if it specifically is a vaultTransferEvent”

 It seems this is something that could have been foreseen and prevented long ago. 

 Creating a secure cross-chain bridge is one of the most important milestones for the industry right now, and the race is on to be the first to provide it. 

 As AAVE have hinted that they will release something soon, it seems that this is a prize even the giants of DeFi cannot resist fighting for.

 If innovation really does lead to exploitation, then there are many more stories yet to be told... 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] PancakeBunny exploit: Two months ago PancakeBunny got rekt on BSC, now the same thing has happened on Polygon

## Summary
Severity: High
Target: PancakeBunny
Loss: $2,400,000
Published: 07/16/2021
Source: https://rekt.news/pancakebunny2-rekt
Type: rekt-postmortem

## Details
## PancakeBunny - REKT 2

 Sunday, July 18, 2021 PancakeBunny - Polygon - REKT 

 read this article also in : zh 

 We sent it back, and then they lost it. 
 How earitating. 

 Two months ago PancakeBunny got rekt on BSC, now the same thing has happened on Polygon.

 $2.4 million lost, and their second entry earned on our leaderboard. (#33) 

 They say there’s a plan to compensate their users, so it seems they’re not ready to give up yet.

 Despite the growing accusations of it being “an inside job”, the PancakeBunny TVL is slowly returning.

 Try not to lose it this time. 

 From the official post-mortem. 

 Attacker’s Address: 0xa6021d8c36b2de6ceb4fe281b89d37d2be321431 

 Attack TX Log: 0x25e5d9ea359be7fc50358d18c2b6d429d27620fe665a99ba7ad0ea460e50ae55 

 The attacker made a small deposit in one of the Bunny Vaults and at the same time, made a large deposit directly to MiniChefV2 (SushiSwap)

 They then called the function withdrawAll to execute the attack, using the amount deposited in the MiniChefV2 as interest.

 The attacker followed the following steps to exploit the polyBUNNY minter: 

 Deposit 0.000000009416941138 SLP (~19,203 USD) into the polygon.pancakebunny USDT-USDC Vault.

 Deposit 0.000023532935903931 SLP (~47,990,975 USD) to the USDT-USDC MiniChefV2 contract on SushiSwap.

 This generated a performance fee of 0.000007006743943544 SLP (~14,284,950 USD) and minted 2.1 million polyBUNNY to the attacker

 Dump polyBUNNY for WETH

 Repay AAVE’s flashloan and exit the attack, gaining 1,281.702952074137533313 ETH.

 The price of polyBunny fell from $10 to $1.78.

 This same exploit was used on “ApeRocketFi” , a direct fork of PancakeBunny, just 2 days ago. 

 ApeRocket lost $260K on BSC and $1M on Polygon, yet PancakeBunny didn’t prevent the same thing from happening to them.

 Was somebody using the smaller protocol as a test, to check that their technique worked? 

 If so, why would they risk alerting PancakeBunny to the loophole? Perhaps somehow they knew that wouldn’t be an issue...

 Of course, it’s possible that the attackers were not the same person, or that they didn’t realise the same attack vector was possible in the original code.

 Somehow that seems unlikely. 

 Who will send money to PancakeBunny now? 

 We wish we hadn’t...

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

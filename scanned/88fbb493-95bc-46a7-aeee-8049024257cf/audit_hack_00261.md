# [C] Team Finance exploit: Four projects got rugged through their shared anti-rug mechanism

## Summary
Severity: Critical
Target: Team Finance
Loss: $15,800,000
Published: 10/27/2022
Source: https://rekt.news/teamfinance-rekt
Type: rekt-postmortem

## Details
## Team Finance - REKT

 Thursday, October 27, 2022 Team Finance - REKT 

 read this article also in : zh 

 Four projects got rugged through their shared anti-rug mechanism. 

 Team Finance , the self-proclaimed “ Industry Leader In Project Security & Automation ”, lost $15.8M of funds that it was supposed to be safeguarding.

 Of the four pools drained, FEG , Caw , and Kondux were the worst hit. Tsuka was also affected, but experienced less price impact due to a secondary liquidity pool on Uniswap v3. 

 The project’s website claims to protect over $2.5B of assets, but considering the low liquidity of their selection of shitcoins, we can consider this claim to be optimistic at best.

 #46 on the leaderboard . 

 Teamwork. 

 Credit: Peckshield 

 The announcement of the hack explained that the exploit targeted “ the audited v2 to v3 migration function. ”

 The vulnerability was contained in one of the Liquidity Locks ’ “bulletproof smart contracts” which allowed projects to migrate locked LP positions from Uni v2 to Uni v3.

 According to Peckshield’s analysis :

 The protocol has a flawed migrate() that is exploited to transfer real UniswapV2 liquidity to an attacker-controlled new V3 pair with skewed price, resulting in huge leftover as the refund for profit. Also, the authorized sender check is bypassed by locking any tokens.

 The breakdown of the loss to each project’s Uniswap v2 pool is as follows: 

 $11.5M CAW

 $1.7M TSUKA

 $0.7M KNDX

 $1.9M FEG

 Exploiter address 1: 0x161cebb807ac181d5303a4ccec2fc580cc5899fd 

 Exploiter address 2 (containing stolen funds): 0xba399a2580785a2ded740f5e30ec89fb3e617e6e 

 Attack tx: 0xb2e3ea72… 

 Attacker’s contract: 0xcff07c4e6aa9e2fec04daaf5f41d1b10f3adadf4 

 The vulnerable migrate() function was included in Zokyo Security’s audit of Team Finance contracts from August this year.

 “DAO tooling” was amongst the most popular buzzwords throughout the last cycle. 

 For small, anon teams working on innovative protocols, it may be tempting to outsource trust to a third party. But given the array of shitcoins “secured” by Team Finance, the vaults seem more likely to be a way for projects to appear trustworthy by proxy.

 Now that it’s clear that trust has been lost. 

 Will this protocol take one for the team and reimburse the victims, or is it every man for himself? 

 There’s no $ in Team. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

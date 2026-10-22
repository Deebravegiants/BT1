# [C] Value DeFi exploit: 2 for 1, that’s Value DeFi: The first protocol to feature twice on the rekt leaderboard

## Summary
Severity: Critical
Target: Value DeFi
Loss: $10,000,000
Published: 05/05/2021
Source: https://rekt.news/value-rekt2
Type: rekt-postmortem

## Details
## Value DeFi - REKT 2

 Thursday, May 6, 2021 Value DeFi - REKT 

 read this article also in : zh 

 2 for 1, that’s Value DeFi: The first protocol to feature twice on the rekt leaderboard . 

 When we first covered Value in November of 2020, they had just lost $7,000,000 after bragging about their “flash loan protection”.

 Back then we learned that Value DeFi did not really know flash loan . Now they have lost another $10,000,000, and we find out that Value DeFi do not really know copy paste either, as they report the exploit was made possible due to losing a line of code by “human error”

 Ten million dollars lost due to basic mistakes by the team, yet the native token $VALUE barely dumped at all.

 The following analysis is taken from the official post-mortem. 

 On May 5th 2021, 3:22 AM UTC, the exploiter re-initialized the pool and set the operator role to himself and _stakeToken to HACKEDMONEY.

 By doing so, the exploiter took control of the pool and called the method governanceRecoverUnsupported() and drained the original stake token (vBWAP/BUSD LP).

 The exploiter then removed 10,839.16 vBWAP/BUSD LP , then burned the LP tokens and received 7342.75 vBSWAP and 205,659.22 BUSD.

 The exploiter then sold all 7342.75 vBSWAP for 8790.77 BNB at 1inch.

 The exploiter used both BNB and BUSD to buy renBTC and used renBridge to move the funds back to BTC, sent to the following address: 1Cm6WGvXQ9EgvvWX5dRsBxE2NvxFjfbcVF 

 The actions can be verified on-chain here .

 The affected pool contract had an initialize() function that should have been activated after deployment.

 The line: initialized = true ; is missing from the function.

 This meant anyone could re-initialize the pool and set themself as owner, thereby taking full control. As owner, the exploiter used the governanceRecoverUnsupported() , which is used for recovering pool funds in the event of a bug or undesired event.

 During set up of the profit-sharing vStake pool, the code was not written from scratch but migrated from the old implementation of the Value DeFi Reserve Fund, which had the correct setting. When merging the code, the line was not included.

 In the end, the hacker was the only one who got their value for their money, a ten million dollar prize without even taking out a loan. 

 The Value DeFi team however, just got another spot on our leaderboard . 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

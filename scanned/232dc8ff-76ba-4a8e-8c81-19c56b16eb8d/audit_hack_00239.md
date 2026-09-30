# [H] Skyward Finance exploit: Skyward Finance has come crashing down to earth

## Summary
Severity: High
Target: Skyward Finance
Loss: $3,200,000
Published: 11/02/2022
Source: https://rekt.news/skyward-rekt
Type: rekt-postmortem

## Details
## Skyward Finance - REKT

 Thursday, November 3, 2022 Skyward Finance - NEAR - REKT 

 read this article also in : zh 

 Skyward Finance has come crashing down to earth. 

 The NEAR-based token launchpad had its treasury drained of 1.1M NEAR, worth approximately $3.2M at the time.

 The exploit caused the price of SKYWARD to tank by ~90%:

 Rather than the usual damage-control and downplaying, the team’s announcement concedes that the exploit “ render[ed] the Treasury and the $SKYWARD token effectively worthless. ”

 Going on to explain that the contracts are fully immutable, the Skyward assured any projects currently launching via the platform that “ existing and previous sales are not affected, so funds and proceeds can be withdrawn safely. ”

 But there was no such good news for Skyward holders:

 We recommend users to withdraw their funds safely where they can and for the community to no longer interact with Skyward.

 Was this incident an honest, albeit simple, mistake?

 Or a planned ejector seat?

 Credit: Sanket Naikwadi , BlockSec 

 Shortly after 5pm UTC yesterday, the exploiter redeemed (previously accumulated) SKYWARD for wNEAR from the treasury using the redeem_skyward function.

 However, the function lacks proper verification of the token_account_ids parameter, allowing the attacker to loop the redemption of wNEAR by repeatedly passing their withdrawal within the transaction.

 The exploiter repeated the exploited redemption process until the treasury had been drained of wNEAR.

 Exploiter’s address: 5ebc5ecca14a44175464d0e6a7d3b2a6890229cd5f19cfb29ce8b1651fd58d39 

 Attack tx: 92Gq7zeh… 

 The fact that it took over a year for anyone to find this relatively simple exploit is remarkable. 

 Perhaps hackers are less familiar with the NEAR ecosystem and feel their time and resources can be put to use more profitably elsewhere…

 Or maybe this was a planned exit-by-exploit, and the users were right to be concerned before launch…

 This is the first leaderboard entry (#88) for a NEAR-based project; let’s hope we can learn something from it… 

 When headed Skyward, don't fly too NEAR to the sun. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

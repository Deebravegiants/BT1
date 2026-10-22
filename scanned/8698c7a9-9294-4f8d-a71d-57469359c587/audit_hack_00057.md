# [C] Cashio exploit: The latest leaderboard entry (#13) comes from the Solana network, where an anonymous attacker used an infinite mint to make Cashio print faster than t

## Summary
Severity: Critical
Target: Cashio
Loss: $48,000,000
Published: 03/23/2022
Source: https://rekt.news/cashio-rekt
Type: rekt-postmortem

## Details
## Cashio - REKT

 Wednesday, March 23, 2022 Cashio - REKT - Solana 

 read this article also in : zh 

 ~$48M CASHed out. 
 The latest leaderboard entry (#13) comes from the Solana network, where an anonymous attacker used an infinite mint to make Cashio print faster than the Fed.

 The exploit began at 08:15 UTC. At 09:59 UTC, Cashio made their announcement: 

 Please do not mint any CASH. There is an infinite mint glitch.

 We are investigating the issue and we believe we have found the root cause. Please withdraw your funds from pools. We will publish a postmortem ASAP.

 Hyperinflation on a crypto timeframe. 

 At least their tagline was accurate. 

 Credit: samczsun, @madergaser, and @siintemal. 

 The root of the infinite mint vulnerability was Cashio’s incomplete collateral validation system. 

 Before accepting tokens as collateral to mint CASH, the contract checks that the tokens to be deposited are correct (the same type of token that the contract holds).

 However, the validation of the LP tokens to be deposited via saber_swap.arrow is incomplete, as the .mint field is never validated.

 This results in the hacker being able to create a fake root contract , which is never validated, and then a chain of fake accounts which each pass validation checks as they are compared only to one another.

 UPDATE (25/03/2022): The hacker also bypassed depositor_source via a similar mechanism, creating a false bank in order to pass the common.collateral verification. Full details here. 

 The hacker was therefore able to use their token as collateral to mint 2B $CASH. 

 Part of the funds were then burned for SaberSwap LP tokens which were cashed out for 10.8M UST and 16.4M USDC, and the remaining 1.97B CASH were swapped for 8.6M UST and 17M USDC on SaberSwap.

 The majority of funds were bridged back to Ethereum, and swapped for >16k ETH (~$48M) which remains in this wallet. 

 Following the attack, the exploiter’s SOL address emitted hundreds of transactions of relatively small amounts of USDC to different addresses. And 3 hours after the exploit began, the hacker left the following message via transaction input data : 

 “Account with less 100k have been returned. all other money will be donated to charity.” 

 As the attacker has handled part of the refund process themselves, perhaps Cashio will decide to continue. 

 We’ll find out for sure in their planned post-mortem. 

 Should we believe the charitable claims of the anonymous attacker, or is this just an attempt to dissuade anyone from trying to track them down?

 Shitcoins stolen to fund the war effort? 

 We’ll watch the wallet to find out. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [C] Woofi exploit: WooFi got taken for a $8.5 Million ride on March 5th, after a flash loan attack on Arbitrum

## Summary
Severity: Critical
Target: Woofi
Loss: $85,000,000
Published: 03/05/2024
Source: https://rekt.news/woo-rekt
Type: rekt-postmortem

## Details
## Woofi - Rekt

 Wednesday, March 6, 2024 Woofi - REKT 

 read this article also in : 

 Nothing to Woo about here. 

 WooFi got taken for a $8.5 Million ride on March 5th, after a flash loan attack on Arbitrum. 

 Spreek who was the first to catch last week’s Seneca Protocol attack, front ran the news on the exploit:

 Wootrade's WooPPV2 contract exploited for a total attacker haul of 8.5m on arbitrum. It is now paused, so no further action is needed. 

 The team didn’t take long to address the issue and paused the pools that were under attack.

 WooFi , self described as “One Dex to rule all chains”, they offer single-sided yields, cross-chain swaps, perps trading and revenue sharing. 

 Looks like they’re the ones who got ruled, doesn’t it? 

 2024 is off to a hot start for Arbitrum attacks, with Radiant Capital , Gamma Strategies and Seneca already getting hit.

 Now that bull season is back, will 2024 make 2023 look like a giant wrestling a midget? 

 Credit: Spreek , Peckshield , Nick L. Franklin , WooFi 

 One of the WOOFi oracles on Arbitrum was exploited using flash loans, which manipulated the price of WOO in order to repay the flash loans at a cheaper price. 

 The attacker manipulated the Woo price to drain funds from the WooPPV2 pool contract. Then drained the pool using the swap function 3 times, stealing about $8.5 million.

 The exploit was caught and contracts paused within 13 minutes. The attacker still managed to get away with a big stash of ETH.
 
Attacker’s address: 
 0x9961190b258897bca7a12b8f37f415e689d281c4 

 Attack tx:

 0x40e1b8c78083fc666cb7598efcecd0ae0af313fc41441386e4db716c2808ce07 

 Attack contract:

 0xD4c633C9A765bC690E1FbA566981c1F4eab52dF0 

 Attack Flow: 

 The stolen funds were sent to this address .

 Woofi sent an onchain message to the attacker, assuming a whitehat executed the exploit and offered a 10% bounty.

 Woofi issued a post-mortem and highlighted the exploit:

 In WOOFi v2, the sPMM system adjusts oracle prices based on trade value to manage slippage and balance pools. However, an error led to a price adjustment outside the expected range and the fallback check, normally executed against Chainlink and didn't cover the WOO token price. 

 The recent addition of a lending market for WOO on Arbitrum, plus relatively low liquidity support for WOO tokens elsewhere on the network, made the exploit economically feasible. 

 Just because your code is audited isn’t a guarantee. Certik most recently audited WOOFi's swap and oracle contracts in October 2022 .

 Immunefi also held a bug bounty in 2022-3 that included their Wooracle. Although the results don’t seem to be public.

 Oracle manipulation and flash loan attacks were not excluded. 

 Woofi went live on Arbitrum in November 2022, looks like somebody found a bug. 

 Woofi said this was their first incident. But going cross-chain has its risks. 

 These risks are becoming more common as we connect more networks across the chains.

 The attack on Woofi underscores the importance of robust security measures, thorough testing, audits, bug bounties and a keen understanding of the complexities of cross-chain operations. 

 The recent addition of a lending market for WOO on Arbitrum, coupled with relatively low liquidity, created a fertile ground for exploitation. 

 Having a novel oracle design that is not widely used, battle-tested and proven to be a cross-chain solution should serve as a reminder not only for Woofi, but any other protocol that tries to reinvent the wheel.

 Bragging about your sPMM design a few hours before someone took advantage of it is pretty ironic. 

 Is using Chainlink price feeds as a fail safe a good idea?

 Given some of these circumstances, is it a surprise they were attacked? 

 It's a wake-up call for the DeFi community, reminding us that no system is immune to exploitation, especially in an environment where the stakes are high and the pace of innovation is relentless.

 Time in our space moves fast, but protocols should slow down at times, especially when they are already live and the risks are more dangerous than in a testing environment. 

 It is much better to catch the mistakes in the lab instead of having them revealed in real time, where bad actors and vigilantes can make an example out of you.

 While Woofi leads us to believe that it was a whitehat that was behind the attack. At the end of the day, what matters is the fact that they were attacked.

 It shouldn’t even matter whether it was the good guys or the bad guys. 

 Does it matter if the person who broke your window was a burglar or a neighbor trying to get in? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

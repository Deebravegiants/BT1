# [C] Saddle Finance exploit: $11M was stolen from Saddle Finance yesterday, with a further $3.8M rescued by BlockSec

## Summary
Severity: Critical
Target: Saddle Finance
Loss: $11,000,000
Published: 12/02/2021
Source: https://rekt.news/saddle-finance-rekt2
Type: rekt-postmortem

## Details
## Saddle Finance - REKT 2

 Sunday, May 1, 2022 Saddle Finance - REKT 

 read this article also in : zh 

 $11M was stolen from Saddle Finance yesterday, with a further $3.8M rescued by BlockSec . 

 This latest attack makes the Curve knock-off take their second position (#43) on our leaderboard , much higher than their rekt.news debut in January of last year.

 Despite claiming that “user funds are safe”, Saddle later clarified they were only referring to the amount that was not stolen. 

 rekt.news can clarify that the $11 million that was stolen, is definitely not safe. 

 Credit: SlowMist and PeckShield 

 The funds were taken from the protocol’s sUSDv2 metapool in which Synthetix’ sUSD is paired with saddleUSD-V2 LP tokens (from the DAI, USDC, USDT pool). 

 The exploit was possible due to a bug in an old version of the MetaSwapUtils library which doesn’t use a VirturalPrice to calculate the value of the LP token during metapool swaps.

 The issue had been fixed in the current version , but the swap calculation was still using the old version.

 The hacker made a series of flash loan assisted sUSD/saddleUSD-V2 swaps in the metapool, manipulating the price of the LP token which could then be swapped back for more sUSD.

 Exploiter’s address, initially funded via Tornado Cash: 0x63341b… 

 Main hack tx for (3375 ETH): 0x2b023d… 

 Second hack tx (for 557 ETH): 0xe7e047… 

 BlockSec whitehat tx for (1357 ETH): 0x9549c0… 

 Though funds have begun to move through Tornado Cash, at the time of writing, the majority remains in the exploiter’s address.

 In November of last year, Saddle published a report on the vulnerability after a $8.2M near-miss for Synapse protocol who were using some Saddle code. 

 BSC-based nerve.fi were also hit via the same attack vector. 

 The resulting fix to the MetaSwapUtils library was made in December but, apparently, the code wasn’t implemented into metapool swaps properly.

 Saddle forking Curve: if it ain’t broke don’t fix it.

 Saddle not implementing their own fix: if it ain't fixed don't use it.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

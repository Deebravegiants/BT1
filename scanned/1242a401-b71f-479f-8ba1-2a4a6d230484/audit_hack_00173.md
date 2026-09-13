# [C] MonoX exploit: Over $31 million stolen, across two chains, via a price manipulation of the project’s native token, MONO

## Summary
Severity: Critical
Target: MonoX
Loss: $31,400,000
Published: 11/30/2021
Source: https://rekt.news/monox-rekt
Type: rekt-postmortem

## Details
## MonoX - REKT

 Tuesday, November 30, 2021 MonoX - REKT 

 read this article also in : zh 

 rekt by their own token. 

 Over $31 million stolen, across two chains, via a price manipulation of the project’s native token, MONO . 

 MonoX , which launched last month on Polygon and Ethereum, is a DEX based on Single Token Liquidity pools. Rather than the standard pool model of paired assets deposited by LPs, MonoX pools function by grouping a deposited token “ into a virtual pair with our virtual cash stablecoin (vCASH) ”.

 One of the benefits that MonoX claimed their virtual pool model brought was streamlined swap routing. 

 How convenient for today’s hacker who, manipulating a pricing bug, was able to inflate the price of the platform's native token and make a streamlined cash-out into the other deposited tokens.

 Two attacks hit the protocol in swift succession. 

 First, ~$19.4M was stolen on Polygon and just 17 minutes later, the same attack vector was used on Ethereum, taking a further ~$12M.

 The team provided a statement via the MonoX Announcements channel on Telegram, and later via Twitter .

 ...A method in the swap contract was exploited and boosted MONO token price to sky high. The attacker then used $MONO to purchase all the other assets in the pool... 

 ...We also really wish to have a chance in talking with the "attacker". We value very much for what we've built for the current and future MonoX, and most importantly our users and their funds; PLEASE reach out to us! 

 Credit: @BlockSecTeam 

 The protocol’s recently -launched MONO token was used in the exploit. The hacker was able to massively inflate its value owing to a bug in the swapTokenForExactToken code in the Monoswap contract ( Polygon , Ethereum ).

 The function _ updateTokenInfo was used to update token prices following swaps through MonoX pools. However, there was nothing to restrict the use of the same asset for both tokenIn and tokenOut . 

 By doing just this with the platform’s native token, the hacker created a loop in which the price of tokenOut would overwrite the price of tokenIn , pumping the price of MONO over the course of many “swaps”.

 Once the price had been manipulated, the attacker cashed out the overvalued MONO for almost all the other tokens deposited in the platform’s Single Token Liquidity pools.

 Both Halborn and Peckshield conducted audits of the Monoswap contract. How did they both miss this simple bug? Was it deliberate, or just careless? 

 Total assets stolen: 

 5.7M MATIC ($10.5M)

 3.9k WETH ($18.2M)

 36.1 WBTC ($2M)

 1.2k LINK ($31k)

 3.1k GHST ($9.1k)

 5.1M DUCK ($257k)

 4.1k MIM ($4.1k)

 274 IMX ($2k)

 Exploit transactions: Polygon , Ethereum .

 Exploit contracts: Polygon , Ethereum 

 Stolen funds: ($31.4M total) Polygon ($19.4M), Ethereum ($12M).

 Over $30M lost on a protocol barely one month old. In fact, the project had passed $30M TVL just 3 days prior to the exploit. 

 While the rate at which projects are now able to attract value is impressive, the insecurity that comes with investing in DeFi is a stark reminder of the immaturity of the space.

 With time, casualties like these build a base of knowledge on which best practises can be established.

 But for now, experiments will continue to be launched.

 And some of them will fail. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

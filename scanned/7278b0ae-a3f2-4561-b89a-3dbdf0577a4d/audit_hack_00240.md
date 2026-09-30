# [C] Snowdog exploit: A “ game theory experiment ” or a new breed of rug pull?

## Summary
Severity: Critical
Target: Snowdog
Loss: $18,100,000
Published: 11/25/2021
Source: https://rekt.news/snowdog-rekt
Type: rekt-postmortem

## Details
## Snowdog - REKT

 Friday, November 26, 2021 Snowdog - Avalanche - REKT 

 read this article also in : zh 

 A “ game theory experiment ” or a new breed of rug pull?

 For many, Snowdog has made this a thanksgiving to forget… 

 Snowdog claims to be “ a decentralized reserve meme coin ”, forked by the anon team at Snowbank from their own project; one of many OHM-forks to have launched recently.

 The premise was to run an 8-day accumulation phase , during which users could stock up on SDOG via minting, staking or market buying.

 Then, a buyback was scheduled which offered SDOG holders the chance to cash out for a share of $44M in MIM, bought using the treasury funds grown during the accumulation phase.

 Following the buyback, the project planned to burn the proceeds, cut staking rewards and renounce contract ownership in order to fix the supply and establish SDOG as the “ meme currency of Avalanche ”.

 This is the first incident we have investigated on Avalanche.

 Was it luck or inside information that led the top $DOGs to success? 

 In the lead-up to last night, SDOG had been trading on TraderJoe at close to $1350. 

 However, claiming they wanted to protect against bots and MEV searchers frontrunning the sale, Snowdog decided to set up a new AMM with an SDOG-MIM pool solely for the purposes of the buyback. 

 adding a simple mathematical challenge to the AMM, it became nearly impossible for bots to quickly adapt and understand how the swap works. Only users using the front-end could swap 

 The front-end was kept password-protected until the moment the buyback went live, and once the liquidity migrated from TraderJoe was added to the pool, it became clear that a massive price hike had been created as the pooled ratios determined a new SDOG price of ~$70k.

 A list of transactions from the first few minutes in the pool can be found here .

 The first two transactions were the clear winners, picking up around 40% of the spoils between them.

 Tx1 - 187.8 SDOG for 10.4M MIM (SDOG price of ~$55k) from this address , funded via FTX the day before.

 Tx2 - 215.1 SDOG for 7.7M MIM (SDOG price of ~$36k) from this address , also funded via FTX the day before.

 These two transactions sold a total of 403 SDOG for approximately $18M, which would have been worth a mere $500k at pre-buyback rates.

 However the “ joy ” referred to in Snowdog’s explanation of the incident quickly turned to “ deception ” for the vast majority of users who were left either selling their tokens below the previous market price or holding while watching their value nosedive.

 36 seconds after the front-end reveal, $SDOG market price was already lower than the market price before buyback ($1200). 

 The report goes on to defend the use of the custom liquidity pool by drawing attention to the number of failed botted transactions at the time of the launch. However, suspicion began to build over the earliest trades, and the likelihood of them being an inside job:

 The two first and most profitable trades are from brand-new addresses ( one , two ), funded within hours of each other on the day before the buyback. The accounts were funded via FTX, so are likely KYC’d.

 The accounts appeared to have prior knowledge that the buyback would happen on a new DEX, not having approved SDOG for trading on TraderJoe in advance but approving the custom pool as soon as it was published.

 The contract’s challengeKey , introduced in order to disrupt sniping bots, is a further source of suspicion given that team members would know the details of this mechanism and have privileged access to the contract directly before the front-end went live.

 Snowbank and Snowdog have attempted to capture the two extremes of the current crypto zeitgeist on Avalanche. 

 Combining dogcoin FOMO with the aim to establish a reserve currency backed by protocol owned liquidity is ambitious to say the least. And the anon team’s attempt to join these two popular but opposing narratives has backfired, given how the Snowdog “ experiment ” has affected Snowbank’s token price .

 That’s one botched buyback, and two projects rekt by the same team. 

 It seems the response to yesterday’s events has tightened Snowbank’s leash with regard to further launches , despite initially using the hype to tease upcoming products .

 As for any future success of SDOG as Avalanche's answer to DOGE, and Snowbank as its reserve currency, only time will tell.

 Was this a gamed buyback, representing a slightly more sophisticated form of the everyday rugpull? 

 Or was it simply the bubble popping on what was never meant to be anything more than an experimental memecoin? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

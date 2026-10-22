# [C] Yearn exploit: Over two years since its first leaderboard entry , Yearn has landed back on rekt.news having lost over $10M

## Summary
Severity: Critical
Target: Yearn
Loss: $11,400,000
Published: 04/13/2023
Source: https://rekt.news/yearn2-rekt
Type: rekt-postmortem

## Details
## Yearn - REKT 2

 Thursday, April 13, 2023 Yearn - REKT 

 read this article also in : zh 

 rekt in prod. 

 …eventually. 

 Over two years since its first leaderboard entry , Yearn has landed back on rekt.news having lost over $10M. 

 Considered by many as one of DeFi’s most reliable, secure platforms, Yearn made it’s name by offering some of the sector’s simplest farming opportunities.

 The immutable yUSDT contract that was attacked was deployed over three years ago, back when Yearn was Andre Cronje’s iearn finance.

 While the strategy was superceded by newer versions, plenty of funds still remained in the original contract. Later Yearn vault contracts are not affected .

 Despite a last-minute warning on Twitter, immutable contracts can’t be saved. 

 Team member storming0x acknowledged the attack before Yearn reassured users that current contracts were unaffected.

 1156 days to spot a multimillion dollar vulnerability in one of DeFi’s longest established protocols. 

 How did it take so long? 

 Credit: Samczsun , OtterSec , SlowMist 

 The attacker exploited a misconfiguration in the iearn yUSDT token contract . 

 The token generated yield via an underlying basket of yield-bearing tokens, including USDT positions on Aave, Compound, DYDX and BzX’s Fulcrum.

 However, since launch, the yUSDT has contained what appears to be a copy/paste error whereby the Fulcrum USDC address was used instead of the Fulcrum USDT contract.

 The exploiter was able to take advantage of the misconfiguration to vastly manipulate the underlying share prices of yUSDT, and mint a large quantity (1.2 quadrillion) of yUSDT using just 10k USDT. 

 Theori’s junomon.eth provided the step-by-step analysis:

 Exploiter address 1: 0x5bac20beef31d0eccb369a33514831ed8e9cdfe0 

 Exploiter address 2: 0x16af29b7efbf019ef30aae9023a5140c012374a5 

 Exploiter address 3: 0x6f4a6262d06272c8b2e00ce75e76d84b9d6f6ab8 

 Attack transaction 1: 0xd55e43c1… 

 Attack transaction 2: 0x8db0ef33… 

 The minted yUSDT was then swapped for other stables totalling $11.4M, BlockSec provided the following breakdown:

 The attacker was funded via Tornado Cash and redeposited 1000 ETH for laundering. At the time of writing, the first two exploiter addresses contain approximately $1.5M of assets each, and address 3 contains 7.4M DAI.

 Certik conducted an audit of iearn finance in Feb 2020, however it appears that only the yDAI contract was investigated. 

 The test in prod attitude, Cronje’s preferred method, has been responsible for plenty of incidents, providing much of rekt.news’ early content. 

 Generally, though, new protocols and features got rekt within hours or days, not years… 

 In the wake of each attack, a decentralised monopoly began to grow. 

 The wider Cronje-verse has experienced enough incidents to have its own leaderboard, as we discussed after CREAM Finance was hacked for the second time, in October 2021.

 Despite the significant losses, it’s lucky that this case only affected an old and deprecated strategy, and didn’t threaten the $450M of TVL across current Yearn strategies.

 As we wrote last time :

 No protocol is too big to fail.

 First Sushi , now Yearn. 

 It’s a big week for DeFi stalwarts getting rekt. 

 Who will be next? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

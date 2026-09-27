# [C] KyberSwap exploit: It’s already been a November to remember… and there’s still a week to go

## Summary
Severity: Critical
Target: KyberSwap
Loss: $48,000,000
Published: 11/22/2023
Source: https://rekt.news/kyberswap-rekt
Type: rekt-postmortem

## Details
## KyberSwap - REKT

 Thursday, November 23, 2023 KyberSwap - REKT 

 read this article also in : 

 It’s already been a November to remember… and there’s still a week to go. 

 OG decentralised exchange KyberSwap is the latest project to fall victim, getting rekt across six chains for a total loss of over $48M. 

 The project’s concentrated liquidity protocol, KyberSwap Elastic, saw its TVL fall from $71M to under $3M. The losses were spread out as follows: >$20M on Arbitrum, $15M on Optimism, $7.5M on Ethereum, $3M on Polygon, $2M on Base and $23k on Avalanche.

 This incident brings the total stolen this month to over $300M ( so far ), including Poloniex ($126M), dYdX ($8M), Kronos Research ($26M), HECO Bridge and HTX ($99M).

 Spreek spotted the hack, which was confirmed within the hour by KyberNetwork :

 As a precautionary measure, we strongly advise all users to promptly withdraw their funds. Our team is diligently investigating the situation, and we commit to keeping you informed with regular updates.

 Honestly, given that the hacker basically left on-chain instructions , it’s probably best to withdraw from any KyberSwap forks, in case of black hat copycats. 

 As well as playing the Bob Ross of smart contract exploiting, the hacker has some shady connections, but nonetheless claims to be keen to negotiate ( after a nap, of course ).

 Is this an exhausted grey hat, inspired by a near-miss of a similar (albeit simpler ) vulnerability , and finally looking to secure a bounty after over six months of work? 

 Or just a bluffing troll? 

 Credit: 0xdoug , BlockSec 

 The attack, which began shortly before 11 PM UTC last night, targeted KyberSwap Elastic (concentrated liquidity) pools. 

 The exploit involved using flash loans to push asset prices into a region of each pool’s liquidity curve where there was no existing liquidity. Then, by executing extremely precise swaps within this region, the exploiter was able to trick Kyber’s code via a precision error.

 That shows just how carefully engineered this exploit was. The check failed by <0.00000000001%

 See 0xdoug’s detailed breakdown here . 

 BlockSec defined the route cause as “ tick manipulation and double liquidity counting ”: 

 In summary, the attackers borrowed a flash loan and drained the pools with low liquidity. By executing swaps and altering positions, they manipulated the current prices and ticks of the victimized pools. Ultimately, the attacker triggered multiple swap steps and cross tick operations, resulting in double liquidity counting and consequently draining the pools.

 Exploiter address 1 ( ARB , OP , ETH , MATIC , BASE , AVAX ): 0x50275e0b7261559ce1644014d4b78d4aa63be836 

 Exploiter address 2 ( ARB , OP , ETH , MATIC , BASE , AVAX ): 0xc9b826bad20872eb29f9b1d8af4befe8460b50c6 

 Example attack tx (ETH): 0x485e08dc… 

 The attacker used the 0x50275 address for execution and 0xc9b82 address for holding stolen funds across all affected chains. BlockSec’s MetaSleuth provided a map of all the attacks. EigenPhi published a list of all transactions. 

 Although the hacker also funded their address on Scroll, the attack never went ahead. 

 Initial funding came from Tornado Cash on Ethereum (via an intermediary address ), which in turn funded the ARB, OP, BASE and (unused) Scroll addresses. MATIC and AVAX funding came from FixedFloat.

 According to KyberSwap’s docs , the current version of Elastic had been audited by ChainSecurity and via a Sherlock contest . 

 The exploiter clearly has on-chain flair, showing their working via tx event logs throughout the attack, leaving charming comments such as “ Step 2, finding liquidity required ”, “ Is it enough? ” and “ Raping Now ”.

 They also sent 1000 ETH on Arbitrum to an address associated with the $16M hack of Indexed Finance in October 2021. 

 While this may be simple misdirection, the move does sound plausibly like the actions of the Indexed hacker, limelight-loving Andean Medjedovic, who has previous in being performatively offensive.

 The timing is also strange, given the recent (thwarted) governance attack on Indexed Finance’s abandoned treasury. While the fallout is ongoing , the initial attempt appears linked to Lazarus .

 However, while many recent hacks have Lazarus written all over them, this incident looks different. 

 Candid on-chain easter-eggs and attempts at misdirection aren’t Lazarus’ style; they don’t waste time planting red-herrings. 

 Instead, they opt to work openly, relying on complex webs of transactions to bore and confuse investigators, or throw them off the scent.

 And if it were Lazarus, they certainly wouldn’t be looking to negotiate… 

 Whoever the hacker may turn out to be, it appears that all hope is not lost. 

 The the following on-chain message was sent from the exploiter’s address upon completion of the attack:

 Dear Kyberswap Developers, Employees, DAO members and LPs,

 Negotiations will start in a few hours when I am fully rested.

 Thank you.

 Perhaps there’s some good news in store for KyberSwap and LPs. 

 Or is the attacker just toying with us all? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

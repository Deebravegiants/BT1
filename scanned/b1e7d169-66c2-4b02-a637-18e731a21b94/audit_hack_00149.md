# [H] Levana Protocol exploit: Perps platform Levana Protocol lost over $1.1M, or approximately 10% of the protocol’s liquidity, to an oracle manipulation attack lasting almost two

## Summary
Severity: High
Target: Levana Protocol
Loss: $1,146,000
Published: 12/13/2023
Source: https://rekt.news/levana-rekt
Type: rekt-postmortem

## Details
## Levana Protocol - REKT

 Friday, December 29, 2023 Levana Protocol - Osmosis - REKT 

 read this article also in : 

 Gradually, then all at once. 

 Perps platform Levana Protocol lost over $1.1M, or approximately 10% of the protocol’s liquidity, to an oracle manipulation attack lasting almost two weeks. 

 The slow burn went unnoticed until network congestion fanned the flames. 

 A disclosure published on Wednesday explained how the majority of the losses were realised when elevated gas costs on the Osmosis network suddenly made the exploit more profitable.

 The sharp increase in losses alerted the team, who responded by pausing the protocol. 

 The exploit started 14 days ago. Over a period of 12 days the attacker succeeded in draining approximately 4% of Levana's LPs.

 The change in PnL was initially attributed to organic trader profits and lack of effective cash and carry on Levana's smaller markets.

 Yesterday the attack increased significantly during Osmosis congestion, draining an additional ~5% from the pools until the protocol was closed from new positions being opened.

 But if it hadn’t been for the increased network traffic… 

 Would they have even noticed? 

 Credit: Levana , Carter L. Woetzel 

 According to Levana’s post-mortem , the attack began on December 13th, before ramping up significantly on December 26th.

 The exploit took advantage of temporary price discrepancies (delta) between oracle updates to place winning trades in “ volatile markets with high leverage ”. 

 Although the attack vector is fairly simple, context is key. 

 Oracle updates are pushed during regular user trades, as well as from Levana’s off-chain update bot, or every 90 seconds. But by timing attacks just right, and ensuring other transactions couldn’t get through, there was a window of opportunity every once in a while…

 During the first stage, profits were minimal, as the exploit relied on a combination of conditions:

 You would have to find, or artificially create, a period where two events coincide: the large price delta in <90 seconds, plus no other interrupting trading or bot activity

 The second, more profitable stage took advantage of a period of congestion on Osmosis; it remains unclear whether this congestion was organic or engineered for the purposes of the attack.

 Whatever the cause, it allowed for more cases in which the exploiter was free to make their loaded bets as regular user txs couldn’t get through. The report explains :

 A bug in the Osmosis fee market code meant that during times of congestion, the provided gas price was generally insufficient for making trades or performing ongoing bot maintenance activities.

 To top it off, the project was subject to an ongoing DDoS attack over the majority of the exploit period, hampering their ability to respond. 

 The markets affected and their losses (totaling $1.146M) are as follows:

 stATOM_USD: $241k

 ATOM_USD: $229k

 BTC_USD: $190k

 ETH_USD: $128k

 TIA_USD: $108k

 *_USDC: $168k + $82k

 The following step-by-step, provided by Carter L. Woetzel , shows the many factors at play. 

 1 Spam txs such that no oracle update txs can get through (from either users or Levana infra)

 2 DDoS backend infra tied to regularly scheduled oracle update txs

 3 Have an intelligent system tracking the delta🔺between the stale data and the actual market pricing that is ready to get pushed

 4 Use a multiexecute tx to go long or short + update the stale data to market pricing - guaranteeing profit for the attacker as they know exactly what the stale price of the oracle is about to get updated to within their multiexecute tx while also comboing it with a long or short guaranteed to be directionally correct.

 5 Because the attacker was the source of congestion, they knew precisely where to submit txs such that they would get accepted by the nodes

 Levana had been audited by both FYEO and Peckshield earlier in the year. However, bugs which rely on external factors such as network congestion don't look to have been within scope.

 The project plans to make users whole via fees and an upcoming airdrop of LVN tokens, and is incorporating a transaction queuing system which will require a fresh oracle price to open positions.

 Even in the autonomous and disembodied world of DeFi, protocols do not exist in a vacuum. 

 Fundamental considerations such as dependencies on external oracles and the reliance on an underlying network’s fee system must be constantly studied and meticulously tweaked to ensure a stable running product.

 And with inscriptions fever spreading across all chains lately, any protocol could find themselves suddenly clogged up. 

 Crafty attackers may attempt to identify similar opportunities, waiting for congestion to hit a critical threshold, and ready to strike on multiple fronts.

 But considering the complexity of this hack, which took advantage of network-level pressures, protocol logic and off-chain systems, all combined with a distracting DDoS attack… 

 Did Levana simply get unlucky?

 Or are we seeing the emergence of even more nuanced and time sensitive attacks? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

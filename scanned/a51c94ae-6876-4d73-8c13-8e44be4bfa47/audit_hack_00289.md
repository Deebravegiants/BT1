# [C] Blizz Finance, Venus Protocol exploit: Two lending platforms, Venus Protocol on BSC and Blizz Finance on Avalanche, have been drained of $13.5 and $8.3M, respectively

## Summary
Severity: Critical
Target: Blizz Finance, Venus Protocol
Loss: $21,800,000
Published: 05/13/2022
Source: https://rekt.news/venus-blizz-rekt
Type: rekt-postmortem

## Details
## Blizz Finance, Venus Protocol - REKT

 Friday, May 13, 2022 Blizz Finance - Venus Protocol 

 read this article also in : zh 

 The Luna fall-out continues. 

 Two lending platforms, Venus Protocol on BSC and Blizz Finance on Avalanche, have been drained of $13.5 and $8.3M, respectively.

 As the LUNA price continued to plummet, the Chainlink price feed used by the protocols became inaccurate, allowing funds to be borrowed against vastly overpriced LUNA collateral.

 Neither project had existing failsafe mechanisms in place, and even though it appears the alarm was raised in advance, preventative measures weren’t established in time to prevent losses.

 With shaky markets, and the first projects falling victim to the failure of LUNA and UST, how far will the damage spread?

 The total collapse of the Terra ecosystem is no longer in doubt. 

 For a short while the whole chain was halted , and several exchanges (Binance, Bybit, eToro, dydx) suspended trading on LUNA and UST.

 Block production on Terra has now resumed , and the chain is active, but it's far from healthy. On-chain swaps are disabled, and IBC channels are closed.

 The failed UST recovery plan crashed the price of LUNA to fractions of a cent, down from an ATH of almost $120, just over a month ago.

 However, the Chainlink oracle, used as a price feed by both protocols to value collateral, contained a minimum price ( minAnswer ) for LUNA hardcoded at $0.10.

 As the price dropped below this, anyone was able to buy up large quantities of LUNA at market price and use it as collateral (valued at $0.10) to borrow funds from the platforms.

 Venus, with a TVL of ~$1B, was (luckily) able to suspend activity before being totally cleaned out. There is currently an active proposal to resume functionality, but with LUNA and UST positions suspended.

 According to the official statement: 

 Venus Protocol also has a Risk Fund that will be utilised to remedy the shortfall that resulted from this event.

 Blizz Finance, however, was unable to react in time, due to their timelock, leaving the protocol wiped out. A glance at the project’s site shows all assets lent out, supposedly on worthless collateral.

 $8.3M of TVL gone in a flash. 

 With both protocols claiming that the blame lies with Chainlink for the “pausing” of their price feeds, Chainlink put out a statement explaining the functionality of the automatic circuit breaker and describing best practices followed by other protocols.

 No protocol is too big to fail. 

 LUNA dropping below $0.10 may have been unthinkable when the Chainlink feed was set up, but as it became clear that LUNA was not going to recover, Chainlink should have updated their oracle’s parameters to reflect reality.

 This incident shows that even using a reputable oracle such as Chainlink is not a silver bullet. The responsibility lies with each project to understand every element of their protocol and integrate everything in a safe and secure way, no matter what the market does.

 Protocols should have measures in place for these unforeseen events, such as their own automated circuit-breakers to pause contracts under such conditions, as suggested in Chainlink’s docs .

 Unfortunately, these two casualties are unlikely to be the last incidents linked to the implosion of Terra. 

 After maintaining radio silence since announcing the plan to nuke LUNA, Do Kwon has just published his thoughts on how the chain should be resurrected.

 The consequences continue, and we still don't know what happened to the $3B of BTC that belonged to the Luna Foundation… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] dForce Network exploit: dForce Network was hit for $3.65M on both Arbitrum and Optimism

## Summary
Severity: High
Target: dForce Network
Loss: $3,650,000
Published: 02/09/2023
Source: https://rekt.news/dforce-network-rekt
Type: rekt-postmortem

## Details
## dForce Network - REKT

 Monday, February 13, 2023 dForce Network - Arbitrum - Optimism - REKT 

 read this article also in : zh 

 dForce Network was hit for $3.65M on both Arbitrum and Optimism. 

 Shortly after 11pm Thursday night (UTC), an attack on two fronts exploited a common reentrancy vulnerability, netting $1.9M on Arbitrum and $1.7M on Optimism.

 The alarm was raised a few hours later, and dForce confirmed the incident after a further 90 minutes. The team then expanded on their original announcement, stating that they had pause all vaults and adding:

 Users' funds supplied to dForce Lending and other vaults are SAFE.

 Good news came a few days later, when the exploiter returned all funds to dForce multisigs.

 However, the read-only reentrancy vulnerability is well-known, having most recently affected Midas Capital and, before that, Market.xyz . 

 As we wrote in the Midas article:

 It’s always a shame to report on losses in DeFi, but especially when they are down to already known issues

 How much more will be lost to this bug? 

 Credit: SlowMist , Peckshield 

 The exploit used flash loaned funds to deposit into Curve’s wstETH/ETH, depositing the LP tokens into dForce’s wstETHCRV-gauge vault. 

 Upon calling the remove_liquidity function, the attacker’s contract exploited the reentrancy vulnerability to manipulate the virtual price, which dForce uses as an oracle for the wstETHCRV-gauge tokens.

 This resulted in the hacker profiting off the liquidation of other users using wstETHCRV-gauge as collateral.

 Exploiter’s address ( OP , ARBI , ETH ): 0xe0d551017c0111ac11108641771897aa33b2817c 

 Attack tx OP: 0x6c197621… 

 Attack tx ARBI: 0x5db5c240… 

 The vulnerability has been well-known for some time. According to ChainSecurity’s original report : 

 On April 14, we informed Curve and affected projects about a read-only reentrancy vulnerability in some Curve pools. More specifically, the value of function get_virtual_price can be manipulated by reentering it during the removal of liquidity.”

 And Curve have provided a known workaround:

 one can call any method which has the nonreentrant lock (removing 0 liquidity is probably the cheapest).

 The attacker's ETH address was funded via Railgun on mainnet, before being used to fund OP and ARBI addresses via Synapse.

 dForce sent transactions ( OP , ARBI ) offering the attacker a bounty via tx input data.

 Fortunately, the hacker responded days later.

 dForce announced that funds had been returned to the project's multisigs and: 

 All impacted users will be made whole, we will announce the details for distribution of the funds over the next few days.

 But this isn’t the first time dForce has got rekt. 

 Back before rekt.news , in what seems like the distant past of April 2020, dForce lost $25M to an ERC-777 vulnerability. Users were reportedly refunded days later.

 More recently, though, Layer 2 networks have been enjoying a boom in adoption. 

 Of the most popular ETH L2s, Optimism is currently the only one with a token, and OP’s recent all time high is a sign of its growing popularity.

 But with increased usage and higher TVL comes extra attention from those who seek to profit by any means necessary... 

 Airdrop hunters are everywhere and, although they may only stick around until they get what they came for, they are generally harmless.

 But speculators aren’t the only ones on the lookout for the next big thing. 

 So far, we have covered relatively few incidents on L2s, but we expect that to change as blackhats seek out new opportunities…

 This won’t be the last L2 entry on our leaderboard . 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

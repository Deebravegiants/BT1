# [M] Midas Capital exploit: The Midas touch has backfired, leaving a $660K hole in one of its pools of Jarvis Network ’s jFIAT assets

## Summary
Severity: Medium
Target: Midas Capital
Loss: $660,000
Published: 01/15/2023
Source: https://rekt.news/midas-capital-rekt
Type: rekt-postmortem

## Details
## Midas Capital - REKT

 Tuesday, January 17, 2023 Midas Capital - Jarvis Network - REKT 

 read this article also in : zh 

 The Midas touch has backfired, leaving a $660K hole in one of its pools of Jarvis Network ’s jFIAT assets. 

 On Sunday, Polygon-based lending protocol Midas Capital was exploited via a flash loan attack on a recently-added collateral type. 

 Both organisations announced the cause of the attack as the use of WMATIC-stMATIC Curve LP token. The read-only reentrancy vulnerability is a known weakness of this type of LP token, and had previously led to a $220k loss on market.xyz in October.

 All that glitters is not gold… 

 Credit: BlockSec , Beosin 

 Midas recently added WMATIC-stMATIC Curve LP token for use as collateral. These tokens have a read-only reentrancy vulnerability which allows the token's virtual price to be manipulated when improperly implemented.

 According to BlockSec’s analysis the attack has 5 basic steps: 

- 
 the calculation of a position's collateral depends on self.D and totalSupply

- 
 self.D is updated after an unexcepted callback, so the four borrows in step 5 to use an outdated self.D.

- 
 the contract burns stMATIC-f before the unexcepted callback, which causes the four borrows in step 5 to use an updated 
```
stMATIC-f.totalSupply()
```
.

 As a result, @MidasCapitalxyz over-estimated the attack contract's position and lent excessive assets to the contract.

 Attacker address: 0x1863b74778cf5e1c9c482a1cdc2351362bd08611 

 Attack tx: 0x00534902… 

 Attacked smart contract: 0x5bca7ddf1bcccb2ee8e46c56bfc9d3cdc77262bc 

 The attacker was able to borrow the following assets against the inflated collateral:

 jCHF: 273,973

 jEUR: 368,058

 jGBP: 45,250

 agEUR: 45,435

 Which were then swapped to ~660k MATIC ($660k) and sent on to Kucoin and Binance. 

 It’s always a shame to report on losses in DeFi, but especially when they are down to already known issues, with simple workarounds . 

 Jarvis Network will cover the (~$350k) shortfall in backing of jFIATs that resulted from the exploit, and Midas Capital have reached out to the hacker in an attempt to negotiate a bounty.

 In a statement to rekt.news, Jarvis Network's founder Pascal Tallarida explained how they plan to deal with the incident going forward:

 As a result of the Midas exploit, the protocol lost 257k jEUR, 237k jCHF and 45k jGBP, and users lost 111k jEUR and 36k jCHF. The jFIATs belonging to the protocol were not collateralized.

 We have decided to do not wait after Midas, and we are working on a plan to re-collateralize the jFIATs the protocol lost, and reimburse the users who were victim of the exploit. We will propose to the Jarvis governance to allocate part of the protocol’s revenus (liquidity provision, lending interests, protocol fee and farming with POL) and part of the protocol treasury to it, and we will ask for the help and support of our community, partners, investors, and “frens”. I have already discussed with many of them and they have expressed their will to support us in this difficult moment, either with or without counterparty. Also, the company which is the main liquidity provider within the protocol, will help, with both its treasury and revenues (±$700k last year with swap fees, interests and market making).

 Then, Midas promised us that they will do right by us, by reimbursing what they can, and by helping us to provide value to the protocol. It could take them a while to do so, but I trust that they will do it.

 This isn’t the first time we have seen a hastily incorporated collateral type leading to a loss, and is unlikely to be the last.

 Let’s hope this rushed decision doesn’t prove to be Midas’ undoing this time… 

 "His senses are captured by the bait, and, thrilled beyond measure, he feasts his greedy eyes on the sight. So Midas, king of Lydia, swelled at first with pride when he found he could transform everything he touched to gold: but when he beheld his food grow rigid and his drink harden into golden ice then he understood that this gift was a bane and in his loathing for gold cursed his prayer." 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

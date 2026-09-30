# [H] Treasure DAO exploit: Swiggity swooty, somebody plundered the Treasure DAO booty

## Summary
Severity: High
Target: Treasure DAO
Loss: $1,400,000
Published: 03/03/2022
Source: https://rekt.news/treasure-dao-rekt
Type: rekt-postmortem

## Details
## Treasure DAO - REKT

 Thursday, March 3, 2022 Treasure DAO - NFT - REKT 

 read this article also in : zh 

 Swiggity swooty, somebody plundered the Treasure DAO booty. 

 ~$1.4M worth of NFTs has been stolen from the largest NFT marketplace on Arbritrum, leaving the OpenSea competitor stranded in deep water.

 Treasure DAO has advised users to delist their NFTs, and the chase to track down the pseudonymous pirate has begun.

 The thefts were made possible due to a logic bug in the Marketplace’s buyItem function, which allowed existing listings to be “bought” for no fee. 

 harry.eth pointed out that: 

 buyItem doesn't check quantity is > 0... exploiter calls buyItem() with zero quantity, pays 0, still receives NFT

 As well as the simple fix which would have prevented the attack: 

 require(_quantity > 0, “Cannot buy zero”);

 Shortly after the bug began to be exploited, the marketplace was paused and transactions started to fail. 

 Co-founder John Pattern said: 

 We will cover the costs of the exploit—I will personally give up all of my Smols to repair this.

 Examples of NFT listings taken can be seen on Treasure DAO’s Marketplace via, for example, the Smol Brains collection’s recent activity . The project’s floor price is approximately 2.5k MAGIC, worth over $9k at the time of the exploit.

 Following the news, the price of MAGIC dipped by around a third, but has since stabilised, down around 10% compared to before the incident.

 In the hours since the attack, on-chain investigators believe they have linked one of the exploiter accounts to ENS and Binance addresses. 

 Many NFTs are also being returned , suggesting that the threat of doxxing is dissuading the attacker from keeping the illiquid stolen assets.

 Treasure DAO eventually released a statement on Twitter : 

 Thank you to the community for your support during the marketplace exploit. It was a difficult moment, but your support speaks volumes about the resilience of the $MAGIC community.

 We are heads down focused on finding the 50 NFTs that remain stolen and making buyers whole.

 Given the almost instant rally in the token price, and the community response , it looks like this incident won’t be sinking the project. 

 But considering the dirt being dug up on those involved with the project, and the amateur error that led to the loss, perhaps Treasure DAO users should seek riches elsewhere… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

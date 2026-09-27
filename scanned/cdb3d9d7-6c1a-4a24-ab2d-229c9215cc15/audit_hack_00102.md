# [H] Exactly Protocol exploit: L2s have been going through something of a rekt-naissance lately

## Summary
Severity: High
Target: Exactly Protocol
Loss: $7,200,000
Published: 08/18/2023
Source: https://rekt.news/exactly-protocol-rekt
Type: rekt-postmortem

## Details
## Exactly Protocol - REKT

 Friday, August 18, 2023 Exactly Protocol - Optimism - REKT 

 read this article also in : 

 L2s have been going through something of a rekt-naissance lately. 

 Exactly Protocol becomes the latest victim of this summer’s on-chain crime spree, after being hit for $7.2M. 

 The lending platform, based on Optimism, was targeted by an exploit which drained users' collateral.

 Peckshield raised the alarm and the Exactly team responded that they were investigating. An update came almost two hours later, stating that the protocol had been paused:

 We're actively investigating a security issue within our protocol. To ensure user safety, the protocol is temporarily paused (you can still withdraw assets). Our team is on top of this and will share more details asap.

 While the losses are heavy, the collateral ( heh ) damage looks to have been even heavier. 

 DeFiLlama shows the project’s TVL to have dropped from $37M pre-hack, to $26M post-hack .

 The figure has continued to drop since, presumably as users who are able to withdraw do so, and sits at less than $11M at the time of writing. The EXA token is also down almost 35% since the hack.

 Will Exactly ever financially recover from this? 

 Credit: BlockSec 

 The attack was made possible due to an insufficient check in the DebtManager contract ( proxy , implementation ) as to whether the market address was valid.

 This allowed the hacker to pass a fake market address, inserting the victim’s address as _msgSender, and thereby drain users’ collateral.

 Exploiter address 1: 0x3747dbbcb5c07786a4c59883e473a2e38f571af9 

 Exploiter address 2: 0xe4f34a72d7c18b6f666d6ca53fbc3790bc9da042 

 Exploiter address 3: 0x417179df13ba3ed138b0a58eaa0c3813430a20e0 

 Attack contract: 0x6dd61c69415c8ecab3fefd80d079435ead1a5b4d 

 Example attack tx: 0x3d6367de… 

 The attacker was funded from Tornado Cash on Ethereum before bridging to Optimism. 

 Of the 4324 ETH (~$7.2M) of total proceeds from the hack, 1500 ETH ($2.5M) have been bridged back to Ethereum, where they remain. 

 BlockSec provided the following chart illustrating the flow of funds:

 Despite extensive audits from four firms (though none since the debtManager contract was uploaded to GitHub ), Exactly Protocol still got rekt. 

 As we’ve said many times before, audits are not a silver bullet. 

 They should be seen as just one, albeit very important, part of an overall holistic security approach.

 But while some bounty hunters find themselves undervalued by projects who don’t want to cough up the cash, we’re sure to stay busy here at rekt.news . 

 Who will be next on the leaderboard ? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

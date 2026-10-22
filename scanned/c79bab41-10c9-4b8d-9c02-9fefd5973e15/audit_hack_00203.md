# [H] Poly Network exploit: Almost two years after topping the leaderboard with a complex hack of over $600M, this time the losses totalled just $4.4M

## Summary
Severity: High
Target: Poly Network
Loss: $4,400,000
Published: 07/01/2023
Source: https://rekt.news/poly-network-rekt2
Type: rekt-postmortem

## Details
## Poly Network - REKT 2

 Monday, July 3, 2023 Poly Network - Bridge - REKT 

 read this article also in : 

 Poly Network is back. 

 Almost two years after topping the leaderboard with a complex hack of over $600M, this time the losses totalled just $4.4M. 

 And the attack was a simple case of a compromised 3-of-4 multisig. 

 When Lazarus knocked Poly off the top spot with the Ronin bridge exploit, 5 of 9 validator keys were compromised. Apparently, Poly still thought that an even lower bar was acceptable.

 The team eventually acknowledged the attack, informing users that bridging services had been paused and making a call for help to the security community. In a follow-up, Poly clarified that “ 57 assets have been affected on 10 blockchains ”

 Prompting flashbacks of the first hack, which at the time totalled more than the entire rest of the leaderboard combined, initial reports used a notional value of $42B of minted assets. 

 But low liquidity on destination chains meant the attacker was only able to cash out a few million. 

 It seems we only ever hear of Poly Network when they’re hacked… 

 …who knew they were even still around? 

 Credit: Dedaub , Beosin 

 In contrast to Poly’s last incident, this time appears to be a far simpler case of compromised keys; three of four multisig signers validated deposit proofs, granting the attacker access to funds. 

 The attack process involved locking a small amount of tokens on one chain, then withdrawing a larger amount on a different chain via forged proofs, repeated for various assets and chains.

 A full, technical post-mortem can be found here . 

 Attacker’s main ETH address: 0xe0Afadad1d93704761c8550F21A53DE3468Ba599 

 Example tx: 0x1b8f8a38… (deposit on ETH), 0x5c70178e… (withdrawal on BSC)

 EthCrossChainManager contract: 0x14413419452aaf089762a0c5e95ed2a13bbc488c 

 Although the notional value of assets minted reached into the tens of billions, the attacker could only access around $4.4M of Poly’s liquidity, with further assets remaining in the attacker’s address.

 A full list of assets stolen by chain is available here . 

 Blockchain bridges create bottlenecks where funds accumulate on either side, often secured by a flimsy threshold of just a few EOAs. 

 Time and again we have seen hundreds of millions lost to just a few signatures. 

 Last time Poly was rekt, on-chain negotiations resulted in a happy ending, as funds were returned and the whitehat offered a Chief Security Advisor role on top of a $500k bounty.

 Luckily, far less was lost in this time. 

 Will Poly learn their lesson? 

 Or will they go for the hat trick? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

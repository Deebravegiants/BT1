# [C] EasyFi exploit: The Polygon (formerly MATIC) network saw $6 million in stablecoins and ~$53 million in EASY tokens taken without any complications, when the mnemonic

## Summary
Severity: Critical
Target: EasyFi
Loss: $59,000,000
Published: 04/19/2021
Source: https://rekt.news/easyfi-rekt
Type: rekt-postmortem

## Details
## EasyFi - REKT

 Tuesday, April 20, 2021 REKT 

 read this article also in : zh 

 The first hack on Layer 2 was EASY. 

 The Polygon (formerly MATIC) network saw $6 million in stablecoins and ~$53 million in EASY tokens taken without any complications, when the mnemonic keys for EasyFi fell into the wrong hands.

 The founder has compared the attack techniques to those used on Hugh Karp of Nexus Mutual - a compromised machine leading to total loss of liquidity.

 How should we react when users' funds are lost in this way?

 There’s no debate between “hack or exploit” in cases like this, however more sceptical readers may consider the term “fraud”.

 The hacker didn’t attack through any holes in the code, and the founder seems to have used reasonable security measures, yet still they end up at number one on the rekt.news leaderboard .

 Is nobody safe? 

 Despite the public announcement of the attack and the fact that the hacker is now holding 2.98 million EASY tokens, the price of the token has not dumped as much as one might expect.

 The price of the token fell only ~20% in the past 24 hours since the hack. This is likely due to the fact that the hacker has not yet started to sell their stolen tokens.

 EASY is a relatively illiquid asset, with an average 24hr trading volume of roughly $10m ($43m in the past 24hr).

 The hacker is now in control of 30% of the total supply, and with little liquidity, there is not much they can do. The founders are also in a tough situation; the EasyFi network has become centralised and controlled by a criminal mind.

 So the hacker takes the number one place on our leaderboard on paper , and also - have they deserved it? 

 The founder of EasyFi writes that; 

 the compromised machine was not used for daily operations and is used solely for the purpose of official transfers.

 If these funds were used for “official transfers”, then they must have been part of some kind of treasury. If so, why would a single user or device have access?
Why wouldn't these tokens be on a Multisig Wallet and / or be secured by a hardware wallet?

 If this admin key was secured by nothing more than a MetaMask hot wallet, then there’s little reason for sympathy. Those who are in charge of other peoples funds have no reason to not use maximum security.

 We await a more detailed post mortem from @AnkittGaur , who will hopefully have more detailed explanations as to how this attack took place.

 It seems EasyFi is hoping for mercy from their attacker, as they published the following open letter in their “ pre-post-mortem ”

 OPEN LETTER TO THE HACKER

 You’ve used very sophisticated techniques to steal a lot of funds from the EasyFi community. EasyFi is a very new project which has received a lot of love & support from its users being the one of early movers on the layer 2 Polygon network.

 We are still at a very early stage and not in a position to make good all the losses in a personal capacity. We care for our community and shall do everything possible at our end to make good all the losses that happened to our users from this theft. We are in great shock and, believe, so as our users who relied on & supported us since inception.

 As the founder of the project, I would urge you to be thoughtful of the hard work gone into building EasyFi so far. I request you to consider returning all funds and discuss the possibility of an appropriate bounty to avoid all the legal trouble in the future. We can consider a clean payout to a white hacker worth 1M USD and not attempt any legal proceedings regarding this incident.

 This protocol had thousands of users, yet the founders used a level of OPSEC that would be considered poor even just for an individual. 

 Although the eventual incident was supposedly caused by an external attacker, EASY token holders were in a precarious situation all along.

 The (single) admin key was capable of draining all the liquidity with no timelock using the “transfer” function shown below.

 Poor OPSEC and a total lack of effort led to this huge loss of funds. 

 Who knows how EasyFi will explain the situation, but there is very little they could say that would shift the responsibility.

 Why would they not use a multisig, or even a hardware wallet? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Acala Network exploit: In response to Acala Network’s announcement on its Spanish-language Twitter account, user @Jaumeelgran reached out to the team with a wallet screensho

## Summary
Severity: High
Target: Acala Network
Loss: $1,600,000
Published: 08/13/2021
Source: https://rekt.news/acala-network-rekt
Type: rekt-postmortem

## Details
## Acala Network - REKT

 Monday, August 15, 2022 Acala Network - REKT 

 read this article also in : zh 

 Edit 16/08/2022: 

 In response to Acala Network’s announcement on its Spanish-language Twitter account, user @Jaumeelgran reached out to the team with a wallet screenshot displaying the vast majority of the erroneously minted aUSD, accompanied by the following message :

 “ Hey, I’m an Acala holder since day one and there’s no risk from me, get in touch with me via official channels, this was a fault of the system, not mine as a user ”

 Luckily the user had triggered the bug by mistake and has been cooperating with the Acala to return and burn the excess aUSD. Other users profited from the same malfunction, amounting to approximately $1.6M in stolen funds. However, while still not back at peg, the price of aUSD has remained above $0.90 since the protocol was reactivated.

 The one billion that wasn’t.

 Tornado sanctions didn’t deter these Polkadot thieves, who tried to steal ~$1.3B in aUSD from Acala Network : the self-proclaimed “DeFi Hub of Polkadot”.

 However, Polkadot plays differently to Ethereum, and the transfers were quickly disabled “until a pending Acala community governance decision resolves the error”. 

 Meanwhile, the aUSD price chart shows an all too familiar pattern…

 Acala has yet to confirm the exact amount that was permanently stolen, as even with the disabled transfers, some funds still slipped through the net.

 Now we wait and we wonder, how much can Acala return or replace? 

 And where should this go on the leaderboard? 

 Acala stated that: 

 "We have identified the issue as a misconfiguration of the iBTC/aUSD liquidity pool (which went live earlier today) that resulted in error mints of a significant amount of aUSD,"

 and… 

 "The misconfiguration has since been rectified and wallet addresses that received the errorneously minted aUSD have been identified, with on-chain activity tracing in respect of these addresses underway."

 Let’s take a look at this “misconfiguration”.

 Credit: @alice_und_bob 

 The misconfigured iBTC - aUSD pool had recently concluded bootstrapping and begun to trade. It was incentivized with aUSD, ACA & INTR.

 However, the incentives.claim_rewards() extrinsic in Acala wrongfully minted $aUSD in exponential amounts (1.3B in total).

 While most of the attention has gone toward the one user who minted 1.2b aUSD (greedy) , at the same time a handful of other users exploited the situation by:

 a) sending $aUSD to Moonbeam.

 b) swapping for $DOT and sending it to Polkadot.

 c) swapping for $iBTC and sending it to Interlay.

 The $iBTC/pool was almost completely drained, but the DOT pool managed to retain some of the value, because it was a DOT - LCDOT pool and users had to go through this route, which mitigated the damage.

 The two wallets that profited the most are listed below.

 23bmUgSeKMD8Y9triphPw5YHuiz3QUJNqcbmb3Eg9QMQDMWN

 253pFTg22JqHbLeLZupexGMDUuXAJLfEriTYkFqvGWPuwcFi

 A few other users extracted value from the misconfiguration, but it is harder to tell if they did so with bad intent.

 In total, $1.6M in “good value” was transferred off-chain, and $4.6M of “bad debt” in the form of wrongly minted $aUSD also left the chain.

 As Acala and Polkadot were able to so easily disable the stolen funds, we’re not left with not much to say. 

 Like the stories of “compromised keys”, we simply wait and see what those in control decide to do.

 Will wrongly minted $aUSD be destroyed?

 Will they have to roll back the chain?

 And where should this story go on the leaderboard?! 

 We’ll let our Telegram group members decide.

 Probably. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

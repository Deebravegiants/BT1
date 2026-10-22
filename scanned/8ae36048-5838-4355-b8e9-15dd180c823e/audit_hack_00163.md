# [M] Merlin Labs - R3KT exploit: A total of $330k was stolen, bringing their TVL (total value lost) to $1,560,000, and putting them on par with Value DeFi as one of the few protocols

## Summary
Severity: Medium
Target: Merlin Labs - R3KT
Loss: $330,000
Published: 06/29/2021
Source: https://rekt.news/merlin3-rekt
Type: rekt-postmortem

## Details
## Merlin Labs - R3KT

 Tuesday, June 29, 2021 Merlin Labs - R3KT 

 read this article also in : zh 

 Merlin’s hat trick. 

 The third time’s a charm for Merlin Finance. 

 Why do people keep going back? 

 A total of $330k was stolen, bringing their TVL (total value lost) to $1,560,000, and putting them on par with Value DeFi as one of the few protocols to be so unsafe that they have three positions onto the rekt leaderboard. 

 “Madam Merlin” wrote the following message in the Merlin Telegram group. 

 Thank you for your patience. It has been identified that this was an economic exploit.

 The Merlin Dev team had deployed the Alpaca single asset vaults onto the Mainnet for testing this morning. This vault was not supposed to be publicly available or ready to launch to the public.

 Via the smart contract, a hacker deposited 0.1WBNB into the vault and then manually transferred 1000BNB into the contract to trick the contract into thinking it has received 1000BNB in rewards, which resulted in the minter producing MERL rewards.

 We thank you for your patience.

 Thank you for your patience?! 

 At this point they should just say sorry. 

 Credit: RugDoc 

 Exploiter wallet: 0x2bADa393e53D0373788d15fD98CB5Fb1441645BD 

 Merlin's reward system gave users Merlin tokens for every $ in performance fees they brought in.

 It was rewarding 35 MERL (~$500 at the time) for every BNB (worth ~$300).

 When calculating the profit of the strategy, it converted the received BNB to WBNB.

 The increase in WBNB balance was then seen as the profit. 

 By sending BNB to the contract directly, it is also converted to WBNB and considered "profit".

 By depositing BNB in the contract, the attacker could harvest and all that BNB would be assumed to be rewardable profit.

 Straight to ETH, then Tornado and it’s gone. 

 It’s hard times at Merlin Labs. 

 Having lost their lead engineer and being forced to advertise the vacancy , it looks like not only has this wizard lost their staff, but also their magic. 

 Must try harder. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

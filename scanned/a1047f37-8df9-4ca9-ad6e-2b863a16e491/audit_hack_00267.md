# [M] The Idols NFT exploit: Narcissus stared at his reflection until it destroyed him

## Summary
Severity: Medium
Target: The Idols NFT
Loss: $324,015
Published: 1/14/2025
Source: https://rekt.news/theidolsnft-rekt
Type: rekt-postmortem

## Details
## The Idols NFT - Rekt

 Thursday, January 16, 2025 The Idols NFT - Rekt 

 read this article also in : 

 Narcissus stared at his reflection until it destroyed him. The Idols NFT protocol learned a similar lesson about self-reflection. 

 Digital mirrors proved just as dangerous as mythological pools when an attacker exploited The Idols' reward system through a simple yet effective manipulation. 

 By making transactions talk to themselves, they drained 97 stETH ($324k) from the protocol.

 The vulnerability lurked in plain sight – transactions where sender and receiver were identical created an echo chamber of infinite rewards. 

 Like the nymph Echo calling out to Narcissus, each mirrored transaction multiplied the damage.

 The Idols team spotted the exploit within two hours, but the ripples had already spread through their stETH reserves.

 In the end, perhaps it's fitting that a project called "The Idols" fell prey to self-reflection. 

 When smart contracts fall in love with their own reflection, who's left to tend the pool? 

 Credit: Tikkala Security , TheIdolsNFT , TenArmorAlert 
 Tikkala Security first glimpsed the reflection of trouble in The Idols' pool around noon on January 14th, spotting an alarming ripple in the IdolMain contract . 

 The protocol's reward system had become entranced by its own image.

 A critical flaw in the _beforeTokenTransfer() function turned the contract into a hall of mirrors , where each self-referential transaction created infinite reflections of unearned rewards.

The exploit's vanity was matched only by its elegance: when a transaction gazed upon itself - sender and receiver address perfectly mirrored - and the balance stood at precisely 1, the reward system would fall into a narcissistic loop. 
 Like Narcissus himself, the contract became trapped in an endless cycle of self-admiration, doling out stETH rewards it should have kept locked away. 

 The attacker, emerging from the depths of Union Chain, understood this fatal attraction. 

 Initial Funding: 
 0x26aba26511874128b2bf075c4d5f801b27a42082c1ce7aa25327f61fa0185981 

 Through a series of self-reflecting transactions, they coaxed the protocol into an expensive form of self-worship.

 One ripple in the pool remains as a reflection of the attacker's artistry.

 Example Attack Transaction: 
 0x5e989304b1fb61ea0652db4d0f9476b8882f27191c1f1d2841f8977cb8c5284c 

 The Idols team spotted their distorted reflection in the pool within two hours, warning users away from the treacherous waters. 

 By the time the waters settled, the attacker had drained approximately 97 stETH from the protocol - a $324k reflection of The Idols' vulnerabilities. 

 The exploit's success hinged on manipulating the claim reward logic.

 According to TenArmorAlert's analysis , the _beforeTokenTransfer() function suffered from a critical oversight - when processing transactions where the sender mirrored the receiver, and the sender's balance was exactly 1, the system would first delete the claimedSnapshots for the sender before claiming the reward for the same address.

 This sequence created a fatal vulnerability: instead of verifying previous claims before issuing new rewards, the function would erase its memory of past distributions.

 Like Narcissus forgetting everything but his reflection, the contract would reset its reward tracking state before processing each new claim. 

 The system essentially developed amnesia about what rewards it had already given out. 

 This fatal flaw created a loop of infinite reflections - each time the system gazed at itself, it forgot what rewards had already been claimed.

 The attacker simply had to repeat this process, watching their stETH balance multiply with each mirror image transaction. 

 The attack unfolded through multiple transactions, each one a perfect reflection of the last. 

 The hacker executed their strategy with the precision of someone who understood exactly what they were looking at.

 Blockchain explorers watched the attacker's address create ripple after ripple across the protocol's surface.

 Attacker Address: 
 0xe546480138d50bb841b204691c39cc514858d101 

 Even their OpenSea profile stands as a looking glass into their activities: 
 OpenSea Account 

 Flow of funds can be found here: 
 Metasleuth Flow of Funds 

 The Idols had positioned itself as more than just another NFT collection. 

 Their 10,000 generative portraits came with the promise of perpetual stETH rewards - each NFT holder entitled to an equal share of the protocol's growing treasury. 

 The treasury was designed to be "monotonically increasing" - a fancy way of saying the stETH principal could never be withdrawn, only the staking rewards earned.

 This mechanism was meant to ensure NFT holders would always have intrinsic value through their proportional claim on future rewards.

 But like Narcissus's pool, what seemed beautiful on the surface concealed dangers in its depths. 

 The same reward mechanism meant to provide perpetual value became the vector for its undoing. 

 The protocol's gaze, fixed too long on its own reflection, failed to spot the fundamental flaw in its reward distribution logic.

 While previous audits by both CertiK and WhiteHat DAO had examined the protocol in early 2022, none of the contract addresses involved in the exploit match those reviewed in the audits.

 Whatever reflection of security those early reviews provided had long since rippled away.

 The damage - 97 stETH drained from a protocol designed never to lose its principal - reveals how even the most elegant reward mechanisms can drown in their own reflection. 

 When smart contracts spend too much time admiring themselves in the mirror, do they forget to check what's lurking beneath the surface? 

 The Idols' security reviews from 2022 might as well be ancient Greek scrolls - their wisdom lost somewhere between audit and deployment. 

 Over two years passed, code changed, and different contracts emerged bearing only shadows of what CertiK and WhiteHat DAO once examined. 

 The protocol's story reads like mythology now: blessed with dual audits at birth, yet cursed to fall prey to its own reflection.

 Their reward mechanism, designed to provide eternal value, instead delivered eternal lessons about the dangers of self-reference.

 Those ancient auditors warned of centralization risks and privilege problems, but nobody could have predicted a protocol's narcissistic tendencies would be its undoing.

 Now 97 stETH sleeps beneath the surface of some hacker's pool. 

 In the end, which reflection proves more dangerous - the one we see in the water, or the one we choose to ignore? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

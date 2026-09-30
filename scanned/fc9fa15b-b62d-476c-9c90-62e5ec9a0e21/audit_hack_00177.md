# [C] Munchables exploit: Rogue dev tried to turn Munchables into Lunchables

## Summary
Severity: Critical
Target: Munchables
Loss: $62,500,000
Published: 03/26/2024
Source: https://rekt.news/munchables-rekt
Type: rekt-postmortem

## Details
## Munchables - REKT

 Wednesday, March 27, 2024 Munchables - REKT 

 read this article also in : 

 Rogue dev tried to turn Munchables into Lunchables. 

 The Blast L2 Big Bang award-winning project Munchables was exploited for $62.5M by a rogue dev. Funds retrieved from dev within a few hours in a rollercoaster ride of a day. 

 Munchables was quick to report that they were compromised on March 26, tracking movements and attempting to stop the transactions.

 Rumors swirled in the Web3 security community about the possibility that Munchables accidentally hired a North Korean developer who never transferred ownership of the smart contracts back to the team.

 ZachXBT went on offense against the rogue dev, in a turn of events that may have saved the day for Munchables and those affected by the exploit. 

 This is the second attack on a Blast protocol in under a week. Super Sushi Samurai was sliced just a few days ago for $4.8M.

 Blast is still a young chain and clearly going through some growing pains, pretty dangerous considering they quickly generated $1.24B TVL , already surpassing Avalanche. 

 Will Blast continue their upward trend or could we continue to see further exploits that could threaten the trust and stability of the entire ecosystem? 

 Credit: ZachXBT , Munchables , Pop Punk , quit.q00t.eth , Pacman 
 The Munchables exploit, resulting in a staggering $62.5M loss, appears to have been meticulously planned by the rogue dev since the initial deployment of the project's smart contract.

 Upon closer investigation by quit.q00t.eth, it was revealed that the Munchables contract was a dangerously upgradeable proxy, and it had been upgraded from an unverified implementation address . 

 The Munchables contract was soon upgraded to a new version with appropriate checks to prevent users from withdrawing more than they had deposited.

 However, prior to this upgrade, the attacker managed to manipulate the contract's storage slots and assign themselves a deposited balance of 1,000,000 Ether. 

 The scammer used manual manipulation of storage slots to assign himself an enormous Ether balance before changing the contract implementation to one that appears legit. Then he simply withdrew that balance once TVL was juicy enough. 

 Attacker Address: 0x6e8836f050a315611208a5cd7e228701563d09c5 

 Contract upgraded March 21: 0xea1d9c0d8de4280b538b6fe6dbc3636602075184651dfeb837cb03f8a19ffc4f

 A few hours after the attack, in an interesting turn of events, ZachXBT, outed the rogue dev .

 Four different devs hired by the Munchables team and linked to the exploiter are likely all the same person. They recommended each other for the job, regularly transferred payments to the same two exchange deposit addresses and funded each other's wallets. 

 Github Usernames: 

- 
 NelsonMurua913 

- 
 Werewolves0493 (Can no longer be found)

- 
 BrightDragon0719 (Can no longer be found)

- 
 Super1114 

 Payment addresses: 

 0x4890e32a6A631Ba451b7823dAd39E88614f59C97 

 0x6BE96b68A46879305c905CcAFFF02B2519E78055 

 0x9976Fe30DAc6063666eEA87133dFad1d5ec27c5E 

 Exchange deposit address: 

 0x84e86b461a3063ad255575b30756bdc4d051a04b 

 0xe362130d4718dc9f86c802ca17fe94041f1cfc77 

 11 minutes later, Munchables announced that the developer had agreed to share the keys for the full Munchables funds without any conditions. 

 Duo Nine highlighted that ZachXBT scared the rogue dev so much, he gave the keys back. 

 Roughly $60.5M funds transferred back to Munchables:

 Transaction 1: 0x69f271f90204ae993200f54676c922fe5ee3e5020a16ae34f589f52d923857f1 

 Transaction 2: 0x381d57aa2d959ff9580ad61cc6549ae3c026eed9ee5b2ea10f9601a186c49a13 

 Transaction 3: 0x62a148877957cbf1ae89cafa144496d99239ee900a3b90194249e6baaa3ddc2f 

 Pacman broke the news that the funds had been secured in a multisig by Blast core contributors. He went on to shout out ZachXBT and samczsun for their support behind the scenes.

 There were rumors within the Web3 community suggesting the rogue dev might be linked to Lazarus , a North Korean hacking group. While there's no official confirmation, this speculation raises intriguing questions about the attacker's motives and methods. 

 Another controversial topic that was floated by the community around the exploit, was the possibility of rolling back the Blast chain, which immediately raised decentralization concerns. 

 Since the funds were returned, the chain rollback idea was dead in the water, but the conversation did open up a can of worms.

 There was an audit completed March 2024 by Entersof. Password for Audit: ESMunc@24!

 Not that the audit helped much with this matter as rogue dev is usually not in the gameplan. 

 Some of these exploit stories are filled with villains and victims, with the occasional hero in the mix.

 Did the heroes save the day this time around? 

 What could have been the biggest hack of 2024, ended up being an inside job that did not clearly go as planned thanks to some vigilante justice. 
 The CEO of Pixecraft Studios mentioned giving the dev a trial hire in 2022, which didn’t even last a month, due to the dev being sketchy af. 

 After that incident, they changed their hiring practices and now collaborate exclusively with trusted recruiters who conduct background checks on candidates. They recommend all crypto teams adopt similar measures to avoid bad actors found on public job boards.

 Whether to dox or not is a hot topic. While the debate over doxxing continues within the crypto community, it's clear that in cases like the Munchables exploit, the practice may serve as a powerful deterrent against malicious actors and protect the integrity of DeFi platforms. 

 As the space evolves, finding a balance between maintaining privacy and ensuring accountability will be crucial in fostering trust among users.

 With ZachXBT being on the case and already having leads, people chatting about simply modifying chain state or rolling back and the rogue dev having no way to transfer funds without being caught, it is no surprise that the exploiter got checkmated so quickly.

 But, this situation could have gone in a different direction and things could have gotten uglier than they ended up. What if Blast ended up rolling back the chain, assuming that they even can?

 This was the 2nd attack on Blast in under a week. It's essential for other protocols on the network to reassess their security measures and remain vigilant against similar threats.

 Will the chain become known as a Blast from the past? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

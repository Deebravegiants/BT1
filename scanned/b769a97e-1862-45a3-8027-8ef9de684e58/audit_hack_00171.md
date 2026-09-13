# [H] Moby Trade exploit: In the vast ocean of DeFi, Moby Trade's pursuit of protocol security ended like Captain Ahab's obsession - with their control slipping beneath the wav

## Summary
Severity: High
Target: Moby Trade
Loss: $1,003,080
Published: 1/8/2025
Source: https://rekt.news/mobytrade-rekt
Type: rekt-postmortem

## Details
## Moby Trade - Rekt

 Monday, January 13, 2025 Moby Trade - Rekt - Private Key Leak 

 read this article also in : 

 In the vast ocean of DeFi, Moby Trade's pursuit of protocol security ended like Captain Ahab's obsession - with their control slipping beneath the waves. 

 On January 8th, a private key leak led to just over $1 million in assets swimming away faster than digital plankton through a whale's baleen. 

 Yet this tale harbors two predators - the original attacker who harpooned their way through ETH and BTC, and a whitehat crew who managed to rescue $1.47M USDC from further depths.

 One smelled blood in the water, the other threw a life raft.

 Through the murky waters of proxy contracts, from Arbitrum's depths to Ethereum's shores, a trail of transactions reveals how quickly security can sink. 

 In DeFi's treacherous seas, when a protocol's private keys become its white whale, who really becomes the hunter - and who becomes the hunted? 

 Credit: Chaofan Shou , Moby Trade , Tony Ke 
 Just as Ahab's obsession with the white whale left him blind to the dangers of the hunt, Moby Trade's faith in their key management left them exposed to predators lurking in the depths. 

 The first ripples of trouble broke the surface when Chaofan Shou spotted movement in the depths - Moby Trade had their hull breached.

 Moby's initial response floated somewhere between damage control and a lesson in humility:

 "We want to emphasize that it was not a security issue related to the protocol's smart contracts - hackers attempted to steal funds by simply upgrading existing smart contracts using stolen proxy private keys." 

 Translation: "Our keys were stolen, but hey, at least our smart contracts worked as intended!" 

 Behind the scenes, a carefully orchestrated attack was already in motion.

 Like any skilled hunter, they first tested their harpoon on Arbitrum Sepolia before striking mainnet's depths.

 Attacker Testing the Waters: 

 0x2a566D111d0a5Be888FEC5F3834434Af3245Bb1b 

 At the helm of this exploit sat a compromised admin key - the digital equivalent of leaving your ship's wheel unattended in pirate-infested waters.

 The assault began with a swift transfer of ownership, setting off a chain of events that would drain two vaults.

 Like a methodical predator, the attacker struck first at the S_VAULT before circling back thirty minutes later for the M_VAULT. 

 Here's how the ship went down… 

 Attacker Address: 
 0x2a566D111d0a5Be888FEC5F3834434Af3245Bb1b 

 Transfer of Ownership: 
 0x9da34da770f1e9c5d5e176578b32710d8e288587d8401582f34a9631edf9be4b 

 S_VAULT Attack Transactions: 

 30,180 USDC: 
 0xfb260f58332034fe203a41b031c41b8461f469e46d5632b33b328f22aed1fb42 

 0.074 wBTC($6,776): 
 0xa64829baf5b83fb6fbebcac334f2c73f6d8ec31a4c8b210538e32105c8ca8566 

 0.786 wETH ($2,376): 
 0x15890f9b4db381875d2e1e606f5c0b39540295f2af7ab34abe4dd4722dde18d2 

 M_VAULT Attack Transactions: 

 206.97 ETH ($625,302): 
 0x78b8900134bb345c16694096a43532d513dffdbeb3f7e154ac280377c35351b8 

 3.70 wBTC ($338,446): 
 0x39e21d38087de0d31a3e6bdae42c2431211c3773ca8ea96956062de393dfa291 

 But the attacker made a fatal mistake - they left an unprotected upgradeToAndCall function in their wake. 

 Enter SEAL911, proving that not all heroes wear capes - some just write better smart contracts and have cooler tech. 

 The white hat team spotted the vulnerable upgrade function faster than a shark smells blood, deploying their own implementation to rescue $1.47M USDC that was still at risk.

 As Tony Ke from SEAL911 put it: "We just automatically hacked the hacker!"

 $1.47M USDC Rescue: 
 0xa247fb0c2a641ad09f3c798c754662ee46ec56ebebc85c17afa397fdeaafe64a 

 A race against time left SEAL911 just 30 seconds behind the original attacker - close, but not close enough to save the WETH, WBTC and USDC already lost to the depths. 

 The final damage report as of press time: 

 207.78 wETH: $627,678

 3.774 wBTC: $345,222

 USDC: $30,180

 Total stolen: $1,003,080

 Amount rescued by SEAL911: $1,470,191

 For the complete trail of over 35 addresses used to disperse the stolen funds, see Moby's detailed post-mortem .

 Before finally bridging through Stargate to Ethereum: 
 0x6a92d4840309f447922114a349984a1d09a51470 

 The waters cleared slowly - first an incident report , then a post-mortem revealing the wreckage. 

 The protocol detailed their damage control as follows. 

 OLP depositors could withdraw their deposits once systems normalized, funded by the team treasury, while options traders would see their positions either compensated at "most favorable value" or returned intact.

 Although, their journey to Berachain mainnet has been "a little bit" shifted.

 Meanwhile, somewhere in the depths of Arbitrum, stolen funds float through Stargate to safer waters.

 Some lessons of the sea, like lost keys and lost limbs, only need to be learned once. 

 Perhaps they're hoping to find their private keys swimming back upstream? 

 SEAL911's rescue operation proves that in DeFi, sometimes you need a white hat to catch a black hat. 

 But when will protocols learn that private keys make better bait than security solutions? 

 In DeFi’s waters, private keys aren’t just bait - they’re chum. And the sharks are always circling.

 The crypto seas remain as dangerous as ever, where one protocol's vulnerability becomes another team's rescue mission.

 At least this time, some white hats were there to throw a life preserver.

 Perhaps next time Moby Trade will remember - in DeFi's ocean, your private keys aren't the only thing that can get harpooned. 

 In these waters, who's really the whale - the protocol that lost its keys, or the predators waiting for the next leak? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

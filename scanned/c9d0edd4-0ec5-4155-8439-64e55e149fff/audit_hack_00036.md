# [C] Beanstalk exploit: $181 million jacked from Beanstalk, but the attacker only kept $76M

## Summary
Severity: Critical
Target: Beanstalk
Loss: $181,000,000
Published: 04/17/2022
Source: https://rekt.news/beanstalk-rekt
Type: rekt-postmortem

## Details
## Beanstalk - REKT

 Monday, April 18, 2022 Beanstalk - REKT 

 read this article also in : zh 

 $181 million jacked from Beanstalk, but the attacker only kept $76M. 

 rekt.news records the damage, not the profit, so this one takes #5 on the leaderboard. 

 A malicious governance proposal was pushed through by a flash loan, and the attacker then voted to transfer all the assets to themself. 

 Another ~24800 ETH into Tornado Cash, and 250K of stolen money into the Ukraine War Fund.

 How much longer can this crimewave last? 

 Credit: Igor Igamberdiev , Peckshield , Kelvin Fichter 

 This was a governance attack made possible through the use of flash loans combined with the absence of a delay on proposal execution. 

 The attacker temporarily acquired sufficient voting power to immediately execute a malicious emergency governance proposal, draining the protocol.

 Though the attack was instant, some preparation was needed: 

 …there's a ~1 day delay for all governance actions in the $BEAN contract. The attacker actually set this whole thing up yesterday when it made two governance proposals. 

 The first proposal (proposal #18) steals all the money in the contract. The next proposal (proposal #19) sends $250k worth of $BEAN to the Ukraine donation address. This Ukraine proposal is named Bip18 (instead of Bip19)... 

 Once the delay had passed, the attack could be executed: 

 The exploiter was funded from the Synapse Protocol bridge [though initially from Tornado].

 They used a flash loan to get:

 350M DAI, 500M USDC, and 150M USDT from Aave;

 32M BEAN from Uniswap v2;

 11.6M LUSD from SushiSwap.

 These tokens were used to add liquidity to Curve pools with BEAN for the governance voting.

 Further, they deployed and voted for a fake BIP-18 that moved all funds from the protocol contract to the exploiter.

 The next step was removing liquidity, repaying flash loans, and converting all received funds into 24.8k WETH ($76M), which went to Tornado Cash.

 Hacker: 0x1c5dcdd006ea78a7e4783f9e6021c32935a10fb4 

 Hacker Contract: 0x79224bc0bf70ec34f0ef56ed8251619499a59def 

 BIP18: 0xe5ecf73603d98a0128f05ed30506ac7a663dbb69 

 Propose BIP18 tx: 0x68cdec0ac76454c3b0f7af0b8a3895db00adf6daaf3b50a99716858c4fa54c6f 

 Peckshield provided a Step by Step 

 Hacker proposes a malicious proposal BIP with initAddress 

 Launch the hack tx: 0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7 

- 
 Flashloan 350,000,000 DAI, 500,000,000 USDC, 150,000,000 USDC, 32, 425,202 BEAN, and 11,643,065 LUSD

- 
 Vyper_contract_bebc.add_liquidity 350,000,000 DAI, 500,000,000 USDC, 150,000,000 USDT to get 979,691,328 3Crv

- 
 LUSD3CRV-f.exchange to convert 15,000,000 3Crv to 15, 251,318 LUSD

- 
 BEAN3CRV-f.add_liquidity to convert 964,691,328 3Crv to 795,425,740 BEAN3CRV-f

- 
 BEANLUSD-f.add_liquidity to convert 32,100,950 BEAN and 26,894,383 LUSD and get 58,924,887 BEANLUSD-f

- 
 Deposit 795,425,740 BEAN3CRV-f and 58,924,887 BEANLUSD-f into Diamond

- 
 Diamond.vote (bip=18)

- 
 Diamond. emergencyCommit(bip=18) and hacker proposed _init contract is executed to get 36,084,584 BEAN and 0.54 UNI-V2_WETH_BEAN, 874,663,982 BEAN3CRV-f, 60,562,844 BEANLUSD-f to hacker contract

- 
 BEAN3CRV-f.remove_liquidity_one_coin 874,663,982 BEAN3CRV-f to get 1,007,734,729 3Crv

- 
 BEANLUSD-f.remove_liquidity_one_coin 60,562,844 BEANLUSD-f to get 28,149,504 LUSD

- 
 Flashloan back LUSD 11,795,706 and BEAN 32,197,543

- 
 LUSD3CRV-f.exchange to swap 16,471,404 LUSD to 16,184,690 3Crv

- 
 Burn 16,184,690 3Cry to get 522,487,380 USDC, 365,758,059 DAI, and 156,732,232 USDT

- 
 Flashloan back 150,135,000 USDT, 500,450,000 USDC, 350,315,000 DAI

- 
 Burn UNI-V2_WETH_BEAN 0.54 to get 10,883 WETH and 32,511,085 BEAN

- 
 Donate 250,000 USDC to Ukraine Crypto Donation

- 
 swap 15,443,059 DAI to 15,441,256 USDC

- 
 swap 37, 228,637 USDC to 11,822 WETH

- 
 Swap 6,597,232 USDT to 2,124 WETH

- 
 Profit 24,830 WETH is sent to hacker

 And then to Tornado. 

 Presumably to avoid suspicion of an inside-job, Publius, the anon behind the protocol, took the decision to reveal their identity as a group of three in a statement published to Discord. 

 Omniscia is keen to point out that this attack fell outside the scope of their audit, however their report does include commentary on the governance contract. 

 Either way, it is surprising that such a vulnerability was not noticed at some point, given that flash loans are not a novel threat to DeFi governance. A delay on execution of on-chain governance proposals is one way to prevent this.

 This incident might encourage bagholders to monitor governance proposals more carefully.

 However, the average user may expect such heavily - shilled projects such as Beanstalk to be under vigilance of more experienced eyes.

 DYOR. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

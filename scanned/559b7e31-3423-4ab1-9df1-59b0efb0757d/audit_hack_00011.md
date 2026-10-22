# [C] Agave DAO, Hundred Finance exploit: Agave DAO , (an Aave fork) , and Hundred Finance , (a Compound fork) , both fell victim to the same reentrancy attack

## Summary
Severity: Critical
Target: Agave DAO, Hundred Finance
Loss: $11,700,000
Published: 03/15/2022
Source: https://rekt.news/agave-hundred-rekt
Type: rekt-postmortem

## Details
## Agave DAO, Hundred Finance - REKT

 Tuesday, March 15, 2022 Agave - Hundred - REKT 

 read this article also in : zh 

 Two forks met the same fate. 

 Agave DAO , (an Aave fork) , and Hundred Finance , (a Compound fork) , both fell victim to the same reentrancy attack.

 2116 ETH ($5.5M) was lost from Agave, and 2363 ETH ($6.2M) from Hundred Finance, giving a total of $11.7M stolen by the anonymous attacker.

 This is the first attack we’ve seen on the Gnosis (xDai) chain, and the first time we’ve seen two protocols be directly targeted like this.

 However, considering the structure of DeFi today, the double damage is not surprising. 

 Forks upon forks create a house of cards. If the code is copied and pasted, vulnerabilities can open up where they're least expected.

 When one fork falls, all others have to check their foundations. 

 Credit: Daniel Von Fange and Mudit Gupta 

 The attacks were made possible due to the design of the xDAI token which contains the function callAfterTransfer() creating a reentrancy vulnerability. 

 Using flash loans as initial collateral, the attacker(s) nested additional borrow functions inside one another, increasing the amount borrowed before the protocol could update the debt balance. Repeating this process led to borrowing assets worth far more than the collateral supplied.

 The attack vector is the same as in the $18.8M case of CREAM Finance last August.

 Agave DAO 

 Exploit tx (March-15-2022 11:25:40 AM +1 UTC) 

 The stolen funds were then sent to the attacker’s ETH address and after a few hours 2116 ETH ($5.5M) were sent to Tornado Cash.

 Hundred Finance 

 Exploit tx (March-15-2022 11:28:40 AM +1 UTC) 

 The stolen funds were then sent to the attacker’s ETH address and after a few hours 2363 ETH ($6.2M) were sent to Tornado Cash.

 While the price of HND hasn’t suffered too badly from the news, AGVE plunged >20%. 

 Forking strong code is not enough to ensure security after changes are made. The idiosyncrasies of each new environment bring new threats. 

 In this case, the Gnosis (xDai) design revealed hidden dangers not considered when porting the protocols from Ethereum.

 Though both projects are forks from foundational DeFi protocols (Aave and Compound), the original projects have strict vetting in place to avoid allowing tokens with reentrancy vulnerabilities to be used as collateral. Additionally, as Mudit Gupta pointed out, following a “checks-effects-interactions pattern” is another way to mitigate such attacks from taking place.

 Another entry on our leaderboard (#35) , and another lesson learned the hard way. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

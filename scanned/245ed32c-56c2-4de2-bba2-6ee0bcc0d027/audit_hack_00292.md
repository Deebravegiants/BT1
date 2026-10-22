# [H] Visor Finance exploit: It is the season of giving, and Visor Finance is going all in

## Summary
Severity: High
Target: Visor Finance
Loss: $8,200,000
Published: 12/21/2021
Source: https://rekt.news/visor-finance-rekt
Type: rekt-postmortem

## Details
## Visor Finance - REKT

 Wednesday, December 22, 2021 Visor Finance - REKT 

 read this article also in : zh 

 It is the season of giving, and Visor Finance is going all in. 
 Visor allowed certain contracts to mint unlimited rewards.

 Yesterday an anonymous actor took advantage of this gift, and withdrew 8.8M VISR from the platform, worth $8.2M at pre-hack prices.

 However, the hacker suffered when dumping VISR via Uniswap’s VISR-ETH pool. 

 -87% 

 rekt.

 Back in June, Visor, a liquidity management protocol for Uni v3 , downplayed the loss of $500k (of its then $3M TVL) in a security breach. 

 Then, last month, the project fell victim to what the Visor team defensively claimed was “ economic arbitrage ”.

 Does “ reliance on spot prices for issuing shares ” not count as a smart contract bug?… 

 What was it this time? 

 Hacker’s address: 0x8efab89b497b887cdaa2fb08ff71e4b3827774b2 

 Funded by Tornado Cash a few mins before the execution of the attack.

 Due to a vulnerable require() check in the vVISR Rewards Contract ’s deposit() function, the hacker was able to mint unlimited shares using their own contract. 

 As long as the hacker passes their own contract as “ from ” and the contract has an Owner() method of msg.sender , then they can mint as many shares as they want to any address using vvisr.mint() . 

 Credit: @storming0x 

 The attacker transferred ownership of the contract to its own address, before executing the exploit transaction, minting 195k vVISR tokens. 

 These were then burned for 8.8M VISR before being swapped via Uniswap v2 for ETH and washed via Tornado Cash in this and 6 subsequent transactions totalling 113 ETH ($450k) so far.

 In their official post-mortem , Visor has proposed a token migration based on a snapshot before the exploit. 

 They also state that:

 “ We are engaged with both Quantstamp and ConsenSys Diligence for December and January audits and this new staking contract will be included. ”

 As the users are to be refunded, it seems the only damage done is to the reputation of the Visor team.

 At least they are gaining experience in post-hack PR… 

 As BlockSec wrote on Twitter:

 “Since last time an attack was called arbitrage, can we call it an airdrop this time?”

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

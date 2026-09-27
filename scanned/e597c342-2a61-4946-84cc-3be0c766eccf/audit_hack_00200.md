# [H] Platypus Finance exploit: Platypus is beginning to look like an endangered species

## Summary
Severity: High
Target: Platypus Finance
Loss: $2,200,000
Published: 10/12/2023
Source: https://rekt.news/platypus-rekt2
Type: rekt-postmortem

## Details
## Platypus Finance - REKT 2

 Friday, October 13, 2023 Platypus Finance - Avalanche - REKT 

 read this article also in : 

 Platypus is beginning to look like an endangered species. 

 A flashloan attack has drained the Avalanche-based protocol of $2.2M, but this isn’t their first time on the leaderboard … 

 In February, Platypus lost $8.5M when its recently-released stablecoin was attacked (also via flash loan).

 The incident wasn’t exactly a blackhat masterclass. 

 The hacker had neglected to code a way to withdraw funds from the attack contract, and BlockSec were able to whitehack 2.4M USDC to be returned. Additionally, shoddy OPSEC led to the hacker being quickly tracked down , and later arrested in France.

 The project was also hit in July for $150k. 

 **This time, after Peckshield raised the alarm, and the losses began to mount up , Platypus acknowledged the incident:

 Due to suspicious activities in our protocol, we have taken the proactive measure of temporarily suspending all pools.

 As we wrote last time:

 Evolution works in mysterious ways.

 But after three exploits in 8 months… 

 …how long until Platypus goes extinct? 

 Credit: BlockSec , Inspex 

 The attack was comprised of three transactions, each of which used flash loans to manipulate the prices within the Platypus LP-AVAX pool . 

 According to BlockSec , the attacker “ manipulated 'cash' and 'liability' which affected the swap price ” via slippage.

 Inspex provided the following step-by-step: 

 1/ The attacker deposits WAVAX to LP-AVAX, and sAVAX to LP-sAVAX increases the liability of both LP contracts.

 2/ The attacker swapped sAVAX to WAVAX to reduce the cash from the LP-AVAX contract.

 3/ The attacker then withdrawn WAVAX from LP-AVAX to remove all available cash from the LP-AVAX contract. This will increase the slippageFrom value, resulting in manipulating the 
```
actualToAmount
```
 value.

 4/ As a result, the attacker swap and take profit from the manipulated slippage.

 Again, as in February, the hacker made a mistake which allowed for the recovery of some ($575k) of the stolen assets. 

 Attacker address 1: 0x0cd4fd0eecd2c5ad24de7f17ae35f9db6ac51ee7 

 Malicious contract 1: 0x4cfb527f51b391ecb1a5197edc7a38160c261b6f 

 Attack tx 1: 0xab5f6242… 

 Attack tx 2: 0x4425f757… 

 Attacker address 2: 0x464073f659591507d9255b833d163ef1af5ccc2c 

 Malicious contract 2: 0xf2c444572a402ec83b7cb64e4a9fc2188f0628f2 

 Attack tx 3: 0x6a09d385… 

 Rescued funds ($575k): 0x068e297e8ff74115c9e1c4b5b83b700fda5afdeb 

 The remaining stolen funds ($1.6M of WAVAX and sAVAX) currently remain in the primary attack contract . 

 Platypus fork Hummus Exchange has also paused contracts in order to avoid a repeat attack. 

 Platypus was audited by both Hacken and Omniscia, but both audits were completed by early January 2022, over three months before the affected contract was deployed .

 It’s been a rough week for Avalanche. 

 Last weekend’s Stars Arena debacle came after a while with barely a peep from the AVAX community. 

 Despite the fact that 90% of funds have been returned, the way the incident was handled (by both the team and Ava Labs’ CEO) left a bad impression.

 Then, news broke that Avalanche’s favourite DEX Trader Joe is being sued by none other than… Trader Joe’s. Who could've seen that coming? 

 With many alternate L1s struggling, and even pivoting to the more active Ethereum L2 ecosystem… 

 …what’s next for Avalanche? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

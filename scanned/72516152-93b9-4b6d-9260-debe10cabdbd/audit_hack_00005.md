# [H] Abracadabra exploit: Yesterday, some on-chain black magic led to two of Abracadabra’s cauldrons springing a leak

## Summary
Severity: High
Target: Abracadabra
Loss: $6,500,000
Published: 01/30/2024
Source: https://rekt.news/abra-rekt
Type: rekt-postmortem

## Details
## Abracadabra - REKT

 Wednesday, January 31, 2024 Abracadabra - MIM - REKT 

 read this article also in : 

 Yesterday, some on-chain black magic led to two of Abracadabra’s cauldrons springing a leak. 

 The lending platform was hacked for $6.5M on Ethereum, and Abra’s Magic Internet Money didn't look so magic after all… 

 BlockSec and Peckshield raised the alarm, with the former also advising users to withdraw their assets. An official acknowledgement came shortly after, with the team promising to attempt to restore the MIM peg:

 To the best of its Ability, the DAO treasury will be buying back MIM from the market to then burn.

 Just over an hour after the attack began the issue had been mitigated, according to an Abra team member. And the team’s efforts brought MIM back up to around $0.95.

 With the stablecoin currently hovering around $0.97… 

 …what dark arts will it take for MIM to fully repeg? 

 Credit: Offside Labs , EXVULSEC , Kankodu 

 The root cause of the exploit was, as initially thought , a rounding issue in the CauldronV4 code. 

 The borrow function in CauldronV4 contracts was vulnerable to manipulation of the part parameter (the user’s share of total debt) via repeatedly borrowing and repaying an asset, taking advantage of the rounding error. For a more in-depth analysis, see here .

 This allowed the attacker drain MIM liquidity from the yvCrv3Crypto and magicAPE cauldrons, taking advantage of the incorrect debt calculation. 

 Step-by-step :

 1 Flashloan MIM token with Degenbox

 2 Donate MIM token to BentoBox by depositing MIM token to BentoBox with recipient is BentoBox itself (this is a part of ERC-4626 first depositor attacker vector)

 3 Repay liabilities for all other users by calling to 
```
repayForAll()
```
. However the repayment is not complete such that the 
```
elastic
```
 value after the repayment is above a threshold 
```
1000 * 1e18
```
. So the attacker needs to manually repay liabilities for other borrowers to decrease borrow elastic to zero

 4 Repeatedly borrow and repay to inflate the share price. Here the vulnerability is well-known as ERC-4626 first depositor (or vault share price inflation)

 5 Add collateral and borrow a large amount of MIM token

 6 Repay flashloan and take profit

 The resulting dump of the stolen MIM (for ETH) caused the depeg. 

 Attacker address: 0x87f585809ce79ae39a5fa0c7c96d0d159eb678c9 

 Attack tx 1 (10:14 UTC): 0x26a83db7… 

 Attack tx 2 (10:26 UTC): 0xdb4616b8… 

 Exploited CauldronV4 contracts:

 yvCrv3Crypto 0x7259e152103756e1616A77Ae982353c3751A6a90 

 magicAPE 0x692887E8877C6Dd31593cda44c382DB5b289B684 

 Funds are currently held in two accumulation addresses: Exploiter address 2 ($4.2M) and Exploiter address 3 ($2.2M). The Abracadabra team have reached out on-chain in an attempt to open negotiations.

 After a busy start to January, and the chaotic ETF approval announcements, the long-awaited TradFi-propelled market turnaround never materialised, and apathy seems to have taken over the timeline.

 Now, a multimillion dollar exploit of one of the last bull run’s key players seems to have made little noise. 

 Abracadabra’s Degenbox was a key part of the overleveraged Anchor play which eventually led to the collapse of LUNA/UST , and co-founder Daniele Sesta is one of only a few of last cycle’s main characters that hasn’t ended up behind bars . 

 A mix of populist calls to ‘Occupy DeFi’ and a talent for ponzi-pivoting saw Frog Nation projects propelled to enormous TVLs off relatively little innovation throughout 2021.

 Even Popsicle getting rekt for $20M and then Wonderland’s Sifu scandal didn’t seem to put the degens off. 

 Yesterday’s hack comes just as new offerings are being teased . 

 A taste of things to come? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

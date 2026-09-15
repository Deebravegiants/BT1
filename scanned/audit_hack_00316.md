# [H] Zunami Protocol exploit: NOTE: This article has been edited to remove reference to Ackee Blockchain, who audited an earlier version of the protocol before the attacked MimCurv

## Summary
Severity: High
Target: Zunami Protocol
Loss: $2,100,000
Published: 08/13/2023
Source: https://rekt.news/zunami-protocol-rekt
Type: rekt-postmortem

## Details
## Zunami Protocol - REKT

 Monday, August 14, 2023 Zunami Protocol - REKT 

 read this article also in : 

 NOTE: This article has been edited to remove reference to Ackee Blockchain, who audited an earlier version of the protocol before the attacked MimCurveStakeDAO strategy was added.

 The Curve ecosystem can't catch a break… 

 Yesterday, Zunami Protocol lost $2.1M as the project’s Ether- and USD-pegged stablecoins came under a price manipulation attack. 

 Although Curve itself was unaffected, the exploiter drained Zunami’s zETH and UZD liquidity pools on Curve, causing the ‘zStables’ to depeg by 85% and 99% , respectively. 

 Peckshield raised the alarm but, after the recent BlockSec/Curve debacle , was careful not to provoke criticism and opted not to provide transaction hashes or addresses.

 Shortly after, Zunami confirmed the exploit:

 It appears that zStables have encountered an attack. The collateral remain secure, we delve into the ongoing investigation.

 First Conic Finance , then JPEG’D, Alchemix and Curve itself , now Zunami… 

 Could the Curve Wars be proving even more lucrative for hackers than for protocols? 

 Credit: Peckshield , BlockSec 

 Just over an hour after the initial alert, and presumably after confirming no further funds were at risk, Peckshield followed up with more detail : 

 It is a price manipulation issue, which can be exploited by donation to incorrectly calculate the price as shown in the following figures.

 The attacker used flash loans to execute large token swaps (e.g. SDT), causing slippage in the pool which could be used to manipulate LP token prices. The root cause was a flawed price calculation via the totalHoldings function. 

 BlockSec provided the following step-by-step:

 The proceeds (1184 ETH or $2.1M) were quickly deposited into Tornado Cash. 

 The protocol itself and the UZD and zETH contracts were audited by Hashex .

 Attacker’s address: 0x5f4c21c9bb73c8b4a296cc256c0cde324db146df 

 Exploit tx (zETH): 0x2aec4fdb… 

 Exploit tx (UZD): 0x0788ba22… 

 The Sushiswap SDT pool, although used by the hacker during the price manipulation, is safe ( despite what a certain relentless bear-poster might like to imply ). 

 Peckshield may have been careful not to include sensitive information in their alert, but others weren’t so cautious . 

 Following BlockSec’s public announcement of the root cause behind the Vyper bug last month, the backlash prompted a debate about how many security firms apparently chase Twitter clout while potentially aiding hackers.

 The discussion, and calls for feedback, appear to have led to tweaked alerting standards which prioritise only the crucial information to alert users who may need to withdraw funds, but without giving away any clues which bad actors may take advantage of.

 Another step forwarded is the SEAL 911 hack hotline ; the Telegram bot aims to use its list of members is a fast-response for any concerned whitehat looking to alert a potentially vulnerable protocol’s team.

 Security teams do important work in DeFi, where exploiters are lurking around every corner. 

 Not least BlockSec, with their impressive whitehacking record . 

 But keeping DeFi safe is a constant game of cat-and-mouse, one that can’t always be won.

 Who will be next to fall prey? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

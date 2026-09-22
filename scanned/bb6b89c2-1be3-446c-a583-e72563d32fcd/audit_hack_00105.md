# [H] Fortress Protocol exploit: Fortress Protocol , the lending arm of JetFuel Finance on BSC, was pillaged for $3M yesterday

## Summary
Severity: High
Target: Fortress Protocol
Loss: $3,000,000
Published: 05/08/2022
Source: https://rekt.news/fortress-rekt
Type: rekt-postmortem

## Details
## Fortress Protocol - REKT

 Monday, May 9, 2022 Fortress - REKT - BSC 

 read this article also in : zh 

 Fortress Protocol , the lending arm of JetFuel Finance on BSC, was pillaged for $3M yesterday. 

 Weak fortifications surrounding the project’s oracle and governance process allowed the invading hacker to pass a malicious proposal and manipulate the price of collateral. 

 Though contracts remain live, the team have paused the platform’s UI and launched a follow-up proposal to repair the damage.

 However with $3M gone, will this leave Fortress in ruins? 

 Credit: BlockSecTeam , Certik 

 The protocol’s price oracle was vulnerable to manipulation as the price submit() function is publicly callable. 

 Coupled with a malicious proposal to add FTS as collateral (with a factor of 700000000000000000), the attacker was able to drain all assets from the platform using just 100 FTS (~4.5$ at pre-hack prices) as collateral.

 The attack was funded with ETH (on BSC), originally sourced from Tornado Cash on mainnet. The funds were then swapped for large quantities of FTS, which were used to reach quorum for the malicious proposal and as collateral.

 Following the exploit, the attacker deposited a total of 1048 ETH ($2.6M) and 400k DAI into Tornado Cash.

 Oracle attack tx: 0x13d198… 

 Attacker’s address on BSC and ETH :
0xA6AF2872176320015f8ddB2ba013B38Cb35d22Ad 

 The project’s site lists ChainLink among its “collaboraters” (sic), however it seems that their oracle expertise was not part of the “collaboration”. 

 Fortress Protocol was audited by both Hash0x and EtherAuthority , two new names on our leaderboard, neither of which picked up any oracle vulnerability in the code.

 Although the attacker was able to pass quorum, their malicious governance proposal was active for 3 days. Why was the suspicious vote not addressed?

 Once again, we see that taking a vigilant role in governance is important, not just for the team but for all users. 

 Will the larger JetFuel Finance ecosystem bail out users for the lost funds? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

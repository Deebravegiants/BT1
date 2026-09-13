# [H] DAO Maker exploit: We didn’t cover the first exploit, but if you get rekt on repeat then we’ve got to say something

## Summary
Severity: High
Target: DAO Maker
Loss: $4,000,000
Published: 09/04/2021
Source: https://rekt.news/daomaker-rekt
Type: rekt-postmortem

## Details
## DAO Maker - REKT

 Monday, September 6, 2021 DAO Maker - REKT 

 read this article also in : zh 

 DAO Maker meets their maker. 
 Again. 

 Less than a month ago they lost $7M. 

 Now they’ve lost another $4M. 

 We didn’t cover the first exploit, but if you get rekt on repeat then we’ve got to say something. 

 Credit: Mudit Gupta 

 DAOMaker’s init() function was left vulnerable, allowing the attacker to reinitialise 4 token contracts with malicious data. Then, the emergencyExit() function was used to withdraw the funds from each.

 The four contracts and the withdrawal transactions are listed below:

 0x6e70c88be1d5c2a4c0c8205764d01abe6a3d2e22 - emergencyExit with 13.5M CAPS

 0xd6c8dd834abeeefa7a663c1265ce840ca457b1ec - emergencyExit with 2.5M CPD, twice 

 0xdd571023d95ff6ce5716bf112ccb752e86212167 - emergencyExit with 1.44M DERC

 0xa43b89d5e7951d410585360f6808133e8b919289 - emergencyExit with approx 20.6M SHO

 After the exploit and swap routine, the attacker then made init() calls on two more contracts. 

 Both contracts, however, had already been called by a new address , whose transaction history shows a series of init()-emergencyExit() calls, extracting millions of SHO, as well as ALPHR and LSS.

 The final four transactions in this address show the extracted tokens being returned, then an ownership transfer; maybe some belated whitehat behaviour, or the devs trying to save what was left. 

 The attacker went on to sell each token: 

 Ternoa: 13.5M CAPS for 378,189 DAI on 1inch

 Coinspaid: 5M CPD for 158,216 DAI on 1inch

 DeRace: 1.44M DERC for 997,833 DAI on 1inch

 Showcase: 20.6M SHO for 67,663 DAI via MetaMask Swap Router 

 Price effects (at time of writing). 

 Ternoa CAPS dropped to -45%, now -11%

 CoinsPaid CPD dropped to -60% and now -25%.

 DeRace DERC dropped to -75% initially, now trading around -25%,

 Showcase SHO trading at approx. -75%

 The prices of all tokens involved have recovered somewhat since the exploit, although not as much as claimed by DAO Maker. 

 The DAO Maker source code is not public. Was it exposed to an outsider, or is there an insider who should not be trusted? 

 Live footage of a DAO Maker developer getting rekt by their own protocol. 

 As Mr Gupta tweeted on Twitter; 

 DaoMaker claimed that they had audits from 3 firms but looking at learn.daomaker.com/audits , 2 of the audits seem to be for unrelated contracts while the third one from @certik_io points to a dead link.

 We await clarification from Certik. 

 Even if all three audits were real and relevant, no hacked protocol should try and pass the blame to their auditors. 

 Good security has to come from the team, not outsourced to an audit company.

 Every step has to be perfect. 

 Hiring, spec design, code reviews, testing, fuzzing, formal verification, bug bounty program, incident handling, the list goes on…

 But perhaps it’s too late for DAO Maker, who will just have to make dao and mend. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

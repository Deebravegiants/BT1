# [H] Punk Protocol exploit: On Aug 10th, Punk Protocol was hacked for $8.95M, ~$5M of which was later returned

## Summary
Severity: High
Target: Punk Protocol
Loss: $8,950,000
Published: 08/10/2021
Source: https://rekt.news/punkprotocol-rekt
Type: rekt-postmortem

## Details
## Punk Protocol - REKT

 Friday, August 13, 2021 Punk Protocol - REKT 

 read this article also in : zh 

 Punk is dead. 

 On Aug 10th, Punk Protocol was hacked for $8.95M, ~$5M of which was later returned.

 The platform planned to offer a DeFi annuity scheme backed by ETH, WBTC and stablecoins.

 Because there’s nothing more “Punk” than a pension plan. 

 Luckily, a whitehat was able to frontrun the transactions and return over half of the funds. 

 But not without taking a million dollars for themselves. 

 The project planned to use a Fair Launch to bring $3M of deposits into 3 stablecoin pools: USDC, DAI and USDT. 

 The Punk post-mortem details the vulnerability that led to the attack, and describes the root cause as a missing Modifier in the initialize() function within the CompoundModel code .

 The hacker used delegateCall() to replace what should have been the protocol’s forgeAddress with their own malicious contract , as a parameter of the CompoundModel’s initialize() function.

 The lack of an “initializer” Modifier meant that the manipulated function was executed despite being associated with an unknown (and in this case malicious) contract.

 With the contract address now updated, the attacker was then able to call withdrawToForge , sending the assets controlled by the CompoundModel directly to the malicious contract, and into their wallet. 

 Although the withdrawal mechanisms are protected by the OnlyForge Modifier, the initialize() function had already defined the malicious contract as the forgeAddress , and as such OnlyForge did not detect any abnormality.

 The stolen USDC was swapped to ETH via 1inch and then sent to TornadoCash in transactions of 100 ETH each. The other assets were not swapped due to the whitehat intercepting them.

 The hacker’s plan only paid off for one of the three pools however, as the owner of a frontrunning bot decided to put on their white hat upon noticing the transactions.

 The saviour made their motives clear via tx input data , and negotiations began via email.

 Original attack tx: 0x7604c7dd6e9bcdba8bac277f1f8e7c1e4c6bb57afd4ddf6a16f629e8495a0281 

 Whitehat frontrun tx: 0x597d11c05563611cb4ad4ed4c57ca53bbe3b7d3fefc37d1ef0724ad58904742b 

 However, the whitehat didn’t manage to stop all the funds from reaching the attacker: 

 Unfortunately, it looks like my frontrun was not perfect, as I did end up sending $3M USDC to the original hacker. Rewriting txs can be tricky.

 Following a brief exchange between the two, the Punk team managed to convince the whitehat that the incident had not been an inside job.

 A bounty of $1M was decided by the protocol’s anonymous ally and after a halfhearted attempt to negotiate, the team eventually agreed, and the remaining ~$5M was returned.

 Approx $1.95M DAI: 0x008dd92f8bcfcee400aed26d13495fbfc8351f9b21289792fc2bb9e771668147 

 Approx $3M USDT: 0xace7c07695ec1bbf917486c3c81ee7de79c04e0309d4f6a149688463e6f83247 

 Punk Protocol states that all recovered funds will go towards compensation efforts for their users, and that they will release an update within the next few days.

 The Punk team is also still hoping for a change of heart from their attacker, although any amount of refund made would be insignificant compared to the previous day's events at Poly Network. 

 Is a white hat white if they refuse to return part of the money they save? 

 Although the anonymous actor only kept 16% of what was stolen, it was still worth $1M when they forced the deal onto Punk Protocol.

 Something is better than nothing, and the Punk team have little reason to be angry at the whitehat, but that money could have gone back to its original owners...

 Anti-heroes are everywhere in DeFi. It's white hat by day, and black by night. 

 Security auditor salaries are nothing compared to what they can earn by using their skills for themselves, and they're given the first and best opportunity to do so.

 Whitehats set their own wages, while security auditors take their salaries and the blame. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

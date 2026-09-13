# [C] PrismaFi exploit: PrismaFi, the self-described end game for liquid restaking, is the first restaking platform to be gamed

## Summary
Severity: Critical
Target: PrismaFi
Loss: $11,600,000
Published: 03/28/2024
Source: https://rekt.news/prismafi-rekt
Type: rekt-postmortem

## Details
## PrismaFi - REKT

 Thursday, March 28, 2024 PrismaFi - REKT 

 read this article also in : 

 PrismaFi, the self-described end game for liquid restaking, is the first restaking platform to be gamed. 

 PrismaFi fell victim to a flash loan attack, resulting in a loss of 3258 wstETH tokens, valued at approximately $11.6 million. 

 Cyvers caught the exploit quickly on March 28th, alerting PrismaFi to check their TroveManager contract.

 PrismaFi commented soon after , informing the community that Core engineering contributors will pause the protocol and investigate. Soon after , PrismaFi instructed vault owners to disable delegate approvals.

 Around 4 hours later, PrismaFi announced that the protocol was paused by the emergency multisig and the remaining funds are safe. They also stated mkUSD and ULTRA, as stablecoins, are overcollateralized and are not at risk. 

 Decurity detected a copy-cat exploit that someone deployed, but not yet used. 

 The market has been waking up from its extended winter, but with that, the attacks are increasing.

 PrismaFi is a fork of the Liquity Protocol , with some changes to the code. Liquity claims the exploit on Prisma is not replicable on Liquity.

 With restaking being a hot trend lately and this being the first exploit on a restaking protocol, could restaking exploits become a hot trend as well? 

 Credit: Cyvers , Prisma Finance , Decurity , ExVul , Nick Franklin 
 According to ExVul's root cause analysis , the exploit occurred due to a vulnerability in the MigrateTroveZap contract. This contract is designed to automate the migration process between different versions of Trove Managers for the same collateral. 

 The contract's onFlashloan() function lacked proper input validation, allowing the attacker to manipulate input data. By doing so, the attacker could trigger the closeTrove and openTrove functions on arbitrary addresses, even those not owned by the attacker.

 In the exploit transaction, the attacker targeted a specific address and closed its trove, resulting in the MigrateTroveZap contract being refunded with 1745 wstETH.

 Subsequently, the attacker opened a new trove, spending 463 wstETH.

 After the onFlashloan callback execution, around 1282 wstETH remained in the MigrateTroveZap contract. The attacker then opened their own trove and called MigrateTroveZap to migrate it, using the remaining 1282 wstETH for their own trove. Finally, the attacker closed the trove and extracted the profits from the exploit.

 The exploiter was able to gain $11.6M after several successful attacks. 

 Attacker Contract: 0xD996073019c74B2fB94eAD236e32032405bC027c 

 Attacker Address: 0x7E39E3B3ff7ADef2613d5Cc49558EAB74B9a4202 

 Attack Transaction: 0x00c503b595946bccaea3d58025b5f9b3726177bbdc9674e634244135282116c7 

 Funds transferred to:

 0x5d0064f3B54C8899Ab797445551058Be460C03C6 

 0x57f7033F84894770F876bf64772E7EBA48990D65 

 0x2d413803a6eC3Cb1ed1a93BF90608f63b157507a 

 Attack flow of funds can be found here .

 One of the addresses where funds were sent, left a message stating “this is a white hat rescue” and asked to contact someone to offer a refund. 

 Nick Franklin highlighted that 5 days before the attack, an address approved the MigrateTroveZap contract for migration here and here . Could this have been prevented? 

 PrismaFi has indicated further steps will include a Post-Mortem and attempts to retrieve funds. No word on a timeline.

 There were 3 audits conducted, MixBytes in September 2023, Nomoi in early 2024 and Zellic in July of 2023. Since the MigrateTroveZap contract migration was within the past week, there is no word on this particular contract being audited recently.

 With a trail of audits in its wake, PrismaFi's MigrateTroveZap contract may have slipped through the cracks. 

 Do you think PrismaFi did their due diligence? 

 In the high-stakes world of DeFi, even the "end game" can be gamified. 
 The PrismaFi exploit marks the first known attack on a restaking protocol, possibly opening Pandora's box for future incidents.

 A part of the story may have yet to unfold, the copy-cat exploit someone deployed, but have yet to use. Could this be foreshadowing? 

 As restaking platforms gain traction, the DeFi community must stay sharp, prioritizing security and constant vigilance against emerging threats.

 The PrismaFi incident serves as another cautionary tale, reminding us that hype and growth can attract bad actors and vigilantes eager to exploit vulnerabilities.

 Granted, new innovations come from experimenting, but trial running in real time, with real funds, as opposed to doing everything possible in a testing environment is a dangerous game.

 As we chase innovation, maybe we are gambling too much with the security of users' funds. 

 Will we learn from our mistakes or continue to play Russian Roulette with our digital fortunes? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

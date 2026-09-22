# [C] Curio exploit: Curio's MakerDAO-based smart contract on Ethereum was exploited for $16 million, due to a critical vulnerability involving voting power privileges

## Summary
Severity: Critical
Target: Curio
Loss: $16,000,000
Published: 03/23/2024
Source: https://rekt.news/curio-rekt
Type: rekt-postmortem

## Details
## Curio - REKT

 Tuesday, March 26, 2024 Curio - REKT 

 read this article also in : 

 Stormy Spring breach. 

 Curio's MakerDAO-based smart contract on Ethereum was exploited for $16 million, due to a critical vulnerability involving voting power privileges. 

 Curio broke the news first, highlighting that the incident only affected the ecosystem on the Ethereum side and all Polkadot side and Curio Chain contracts remain secure.

 The exploit wasn't limited to minting and manipulating governance. It extended into sophisticated financial strategies involving token swaps and cross-chain transfers. 

 The exploiter is still holding 996 Billion CGT . The total loss is significant, but difficult to calculate, because of the limited market liquidity of CGT. 

 Could this just be the beginning of storm season? 

 Credit: Curio , Hacken 
 The Curio Ecosystem, known for bridging the gap between tradfi and defi through tokenized real-world assets, got thunderstruck for a $16M loss over the spring weekend.

 On March 23, 2024, CurioDAO Association announced its voting protocol experienced an exploit involving a smart contract based on MakerDAO’s fork. 

 Hacken posted a thread outlining the cause of the exploit.

 As Hacken explained:

 The attack was initiated through the "cook" function of an attack contract, which played a crucial role in leveraging the "IDSChief" and "IDSPause" contracts to execute a governance manipulation and mass token minting scheme. 

 The attacker leveraged this vulnerability by acquiring a small number of CGT tokens, thereby gaining access to elevate their voting power within the project’s contract.

 By locking these tokens and voting, they gained control, allowing them to execute a delegate call to a malicious contract. 

 The exploit not only involved minting tokens and manipulating governance but also complex financial strategies such as token swaps and cross-chain transfers, likely in an attempt to distribute and disguise the origin of the minted tokens..

 The various swaps and transfers indicate a methodical plan to distribute and perhaps obscure the trail of the minted tokens across multiple platforms and blockchains. 

 Attacker Address: 0xdaAa6294C47b5743BDafe0613d1926eE27ae8cf5 

 Attacker Transaction: 0x4ff4028b03c3df468197358b99f5160e5709e7fce3884cc8ce818856d058e106 

 Attack Visualization on Metaseluth. 

 Despite the incident within the CurioDAO, the impact was confined to the Ethereum side of Curio’s technology stack.

 CurioDAO released an exploit recovery strategy on March 25, highlighting a 2 stage compensation plan: 

 - The Curio team will release a new token CGT 2.0 instead of the current CGT token that is susceptible to exploit attacks. 

 - A funds compensation program related to the second token in the liquidity pools will be launched. The compensation program will consist of 4 consecutive stages, each lasting for 90 days. 

 They will be developing and deploying a patch to address the identified vulnerability in the voting power privilege access control. Claiming this patch will undergo rigorous testing to ensure its effectiveness in mitigating similar exploits in the future.

 Along with that, they plan to enhance Curio DAO's smart contract security through upgrades that enforce stricter access controls, audit the code, and add extra layers of security validation to avoid future exploits.

 No known audits could be found and it appears Curio may be doing their security in house. 

 It was mentioned in the exploit recovery strategy, Curio is relying on internal expertise and leveraging best practices in smart contract development and security auditing. 

 Curio DAO is offering a reward structure to white hat hackers, based on proceeds from the initial recovery phase, 10% of the proceeds recovered during the first week and 5% after that, until May 25th.

 Do you believe Curio would have been better protected by having external audits, instead of keeping things in house? 

 Spring brought more than just flowers for Curio, not only wiping out $16M, but essentially retiring their original CGT token. 
 On the bright side, CurioDAO's two-stage compensation plan with a new token, CGT 2.0,may patch things up a bit.

 While Curio claims the exploit was contained to their Ethereum playground, the exploiter is still sitting on 996 Billion CGT tokens. 

 Maybe the attacker just got started and will find a way to swap across chains for a complex financial game. 

 Will Curio's promise to revamp smart contract security calm any brewing distrust? Time will tell.

 If they’re going to keep security in-house, it may not be the best strategy, as highlighted by this attack.

 Launching projects into the wild without proper security due diligence is setting yourself up for failure. 

 Are finding risks after the fact becoming too common, or just an indication that the industry needs to invest more in preventive measures and proactive security strategies? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

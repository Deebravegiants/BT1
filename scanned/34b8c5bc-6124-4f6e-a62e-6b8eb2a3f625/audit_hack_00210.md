# [C] Radiant Capital - Rekt II exploit: Radiant Capital's future has dimmed following a catastrophic security breach

## Summary
Severity: Critical
Target: Radiant Capital - Rekt II
Loss: $53,000,000
Published: 10/16/2024
Source: https://rekt.news/radiant-capital-rekt2
Type: rekt-postmortem

## Details
## Radiant Capital - Rekt II

 Thursday, October 17, 2024 Radiant Capital - Fork - REKT 

 read this article also in : zh 

 Radiant Capital's future has dimmed following a catastrophic security breach. 

 The multi-chain lending protocol suffered a devastating attack that drained over $53 million from user wallets. 

 It appears that compromised private keys left Radiant's defenses in tatters.

 Markets frozen, users reeling, damage still being tallied and this will be one hell of a post-mortem.

 This marks the second major incident for Radiant in 2024, following a $4.5 million flash loan exploit earlier this year. 

 Could this be the final nail in Radiant Capital's coffin, or can they somehow rise from these ashes? 

 Credit: Ancilia , Radiant Capital , Hacken 
 The attack on Radiant Capital unfolded with surgical precision, exploiting a critical weakness in the protocol's multi-signature setup. 

 Blockchain security firm Ancilia first spotted suspicious activity on Radiant's BSC contract, warning users to revoke approvals as $16M had already vanished.

 Radiant Capital remained silent for two hours before finally acknowledging the attack on BSC and Arbitrum.

 They announced collaborations with security firms and paused markets on Base and Mainnet.

 Radiant also recommended revoking access to the following contracts: 

 ARB: 
 0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1 

 BSC: 
 0xd50Cf00b6e600Dd036Ba8eF475677d816d6c4281 

 BASE: 
 0x30798cFe2CCa822321ceed7e6085e633aAbC492F 

 ETH: 
 0xA950974f64aA33f27F6C5e017eEE93BF7588ED07 

 This was no ordinary hack, but a masterclass in exploiting centralized control points within decentralized finance.

 Radiant's security hinged on an 11-signer multi-sig wallet, a setup that should have provided robust protection. 

 However, the devil was in the details: only 3 signatures were required to execute transactions. This low threshold proved to be Radiant's Achilles' heel.

 The attacker, demonstrating an alarming level of access, managed to gain control of at least 3 of these signers. 

 With this foothold, they swiftly executed a three-step plan that would make any black hat hacker proud: 

- 
 Transfer ownership of the lending pools to their malicious contract

- 
 Upgrade the implementation of the lending pools

- 
 Drain funds from the compromised pools

 Despite Radiant's use of a MultiSig wallet for security, the attacker managed to gain control and execute a meticulously planned exploit.

 The attack unfolded across multiple chains, with evidence suggesting weeks of preparation.

 The attacker's first move was to transfer ownership of the Pool Provider contract, which manages Radiant's various lending pools, to a malicious contract. 

 This attack was executed on both BSC and Arbitrum: 

 Attack Transaction on BSC: 
 0xd97b93f633aee356d992b49193e60a571b8c466bf46aaf072368f975dc11841c 

 Attack Transaction on ARB: 
 0x7856552db409fe51e17339ab1e0e1ce9c85d68bf0f4de4c110fc4e372ea02fb1 

 Attacker Address 1: 
 0x0629b1048298AE9deff0F4100A31967Fb3f98962

 Attacker Address 2: 
 0x97a05becc2e7891d07f382457cd5d57fd242e4e8

 The exploiter used DEXs such as 1inch, ParaSwap, PancakeSwap, and Odos to swap for some ETH and BNB, before moving funds to the following wallets.

 Stolen funds moved to Address on ARB: 
 0x8B75E47976C3C500D0148463931717001F620887

 Stolen funds moved to Address on BSC: 
 0xcF47c058CC4818CE90f9315B478EB2f2d588Cc78 

 The malicious contract, used as the implementation for the proxy upgrade, was deployed 14 days ago on several chains. 

 Malicious Contract on BSC: 
 0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5

 Malicious Contract on ARB: 
 0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5 

 This two-week gap between deployment and execution suggests a carefully orchestrated plan, with the attacker biding their time for the perfect moment to strike.

 Interestingly, blockchain data revealed by Hacken point to an attempted exploit on Arbitrum six days prior to the successful attack. 

 Failed Attack on ARB: 
 0xab34055320676b35d4c6c5936dabc4101b45eda0d66b94ee02f10a96e8a1dd45 

 This failed attempt provides insight into the attacker's persistence and willingness to refine their approach.

 Moreover, the same malicious contract was deployed on Ethereum and Base, though these weren't utilized in the attack.

 Malicious Contract on ETH: 
 0x3C2Bc83Dcd293Cc8a23526A37aaeEdD83eBd62de

 Malicious Contract on BASE: 
 0x57ba8957ed2ff2e7AE38F4935451E81Ce1eEFbf5

 The attacker's ambition wasn't limited to a two-chain heist. Malicious contracts lay dormant on Ethereum and Base, like digital time bombs waiting for their moment.

 It seems our enterprising hacker had dreams of a cross-chain apocalypse, thwarted only by Radiant's belated realization that they were being gutted like a fish.

 This wasn't just an attack, it was a master class in DeFi demolition.

 Our "friend" came prepared with a Swiss Army knife of exploits, ready to carve up Radiant's entire multi-chain buffet. 

 In this multi-chain feast of vulnerabilities, who's next on the menu? 

 Radiant Capital's multi-chain dreams have turned into a cross-chain nightmare. 

 With over $53 million evaporating faster than you can say "not your keys" the protocol's future looks about as bright as a black hole. 

 This isn't just a flesh wound – it's a full-body amputation.

 Radiant's "robust" 3-of-11 multisig turned out to be as secure as a paper lock on a bank vault.

 The attacker didn't just find a chink in the armor; they waltzed through the front door with VIP access. 

 The hacker's two-week preparation period suggests they had more patience than Radiant had security. 

 While the protocol was busy expanding across chains, the attacker was meticulously laying out the welcome mat for their own personal heist party.

 Radiant's second major incident this year begs the question: is this a case of lightning striking twice, or just shoddy electrical wiring?

 With their reputation now resembling Swiss cheese, Radiant faces an uphill battle to regain user trust – if there's anyone left to trust them. 

 As users flee the smoldering ruins of yet another DeFi disaster, will they ever feel safe venturing into multi-chain protocols that forgot to install the guard rails? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Pike Finance exploit: Pike Finance swims in turbulent waters, storage vulnerability nets hackers over $1.9 million in multiple attacks

## Summary
Severity: High
Target: Pike Finance
Loss: $1,900,000
Published: 04/30/2024
Source: https://rekt.news/pike-rekt
Type: rekt-postmortem

## Details
## Pike Finance - Rekt

 Friday, May 3, 2024 Pike Finance - REKT 

 read this article also in : zh 

 Pike Finance swims in turbulent waters, storage vulnerability nets hackers over $1.9 million in multiple attacks. 

 The latest exploit caught by Chain Aegis on April 30, resulted in the loss of over $1.6 million in ARB, OP and ETH. Pike Finance confirmed shortly after. 

 This incident followed a previous exploit related to a USDC vulnerability reported just days earlier.

 Pike Finance acknowledged the initial attack , but it wasn’t enough.

 Unfortunately, the actions taken by Pike Finance after the initial exploit left the protocol open to further attack.

 Another attack that could have been prevented. 

 Does Pike Finance have what it takes to navigate these troubled waters? 

 Credit: Quill Audits , Pike Finance , Chain Aegis 

 Fool me once, shame on you. Fool me twice , shame on me. 

 Pike Finance got played for the fool, falling victim not once, but twice to exploits that allowed attackers to seize control and siphon funds from the protocol.

 Pike is a universal liquidity market that enables lending and borrowing using native assets directly on their respective blockchains, eliminating the need for wrapping and cross-chain transfers.

 According to Pike Finance , the initial exploit on April 26 was caused by weak security measures in Pike's contract functions when handling CCTP transfers. 

 During protocol pausing attempts, an added dependency in the code altered storage layout and moved the initialized variable, causing contract misbehavior. 

 Seizing this opportunity, attackers upgraded spoke contracts without admin access, successfully siphoning off funds.

 The upgraded implementation contract of the target contract has a vulnerability, which allows the attacker to initialize and then steal the owner permissions.

 In addition to the attack on Ethereum, the attacker also carried out attacks on Arbitrum and Optimism. 

 The two attacks stemmed from the same smart contract vulnerability, which allowed the attacker to override the contract. 

 Attack Process by Quill Audits : 

- 
 The attacker exploited the initialize function in the original contract, adding their address to the _isActive variable.

- 
 Taking advantage of unprotected initializer functions, the attacker bypassed security measures meant to prevent multiple executions.

- 
 By leveraging version numbers, the attacker consumed and blocked reusable numbers, enabling them to execute new initialization steps with each upgrade.

- 
 Finally, the attacker performed an upgradeToAndCall, implementing a malicious version of the contract and successfully breaching Pike Finance's security.

 April 26 Attack on Arbitrum 

 Attacker:

 0xAdaF1626aEC26A7937aE7d1Fa0664e6E0904C1d0

 Target Contract:
 0x7856493B59cdb1685757A6DcCe12425F6a6666a0 

 Attack Transaction:

 0x979ad9b7f5331ea8034305a83b5cd50aea88adec395fff8298dd90eb1b87667f 

 April 30 Attack on Multiple Networks 

 Attacker:
 0x19066f7431df29a0910d287c8822936bb7d89e23 

 Attack contract:
 0x1da4bc596bfb1087f2f7999b0340fcba03c47fbd 

 Target contract:
 0xfc7599cffea9de127a9f9c748ccb451a34d2f063 

 Attack Transaction on Optimism:
 0x19066f7431df29a0910d287c8822936bb7d89e23 

 Attack Transaction on Arbitrum Transaction: 0x19066f7431df29A0910d287C8822936Bb7D89E23 

 Attack Transaction on Ethereum:

 0xe2912b8bf34d561983f2ae95f34e33ecc7792a2905a3e317fcc98052bce66431

 There are no public audits or bug bounty programs for Pike Finance, both sections in their site docs state “Coming soon”. 

 They have yet to even update their contracts page and currently just list the test net contracts. 

 Pike had a community presale for their native PIU token at the end of March that generated $6.45 million.

 They reached out to the initial exploiter on April 26 in an onchain message .

 They are offering a 20% reward for the return of the funds, or information leading to the recovery of funds.

 In addition, a report and plan to make users whole will be provided at a later time.

 According to many responses to the exploit announcement , many users want their presale funds back, which appear to be unaffected at this time. 

 Will the team get their act together, or end up doggy-paddling in a sea of mistrust? 

 Pike Finance’s security woes raises red flags and makes one wonder, are they winging it or sinking it? 

 The absence of public audits and bug bounty programs, coupled with their failure to secure contracts after the initial exploit, paints a picture of negligence.

 The slow response to the first attack enabled a second, putting its user base at risk, thanks to the sheer carelessness in handling the contracts. 

 Investors, particularly those who participated in the $6.45 million token presale, are understandably worried.

 Pike's delayed updates and vague promises of a "report and plan" do little to ease their fears.

 Can Pike navigate these stormy waters, or will their cavalier attitude towards security sink them? 

 Only time will tell if Pike Finance can right the ship or if they'll serve as yet another cautionary tale of cutting corners in the world of crypto security. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

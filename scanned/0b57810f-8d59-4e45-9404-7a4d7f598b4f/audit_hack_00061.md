# [M] Clober Dex exploit: Clober DEX's Liquidity Vault bled $500k yesterday when attackers exploited a vulnerability as old as DeFi itself - reentrancy

## Summary
Severity: Medium
Target: Clober Dex
Loss: $500,000
Published: 12/10/2024
Source: https://rekt.news/cloberdex-rekt
Type: rekt-postmortem

## Details
## Clober Dex - Rekt

 Wednesday, December 11, 2024 Clober Dex - Reentrancy - Rekt 

 read this article also in : 

 Clober Dex got clobbered. 

 Clober DEX's Liquidity Vault bled $500k yesterday when attackers exploited a vulnerability as old as DeFi itself - reentrancy. 

 The protocol's team had rolled out fresh code changes without proper security review, accidentally leaving their vault door wide open.

 Trust Security and Kupia had done their due diligence, auditing the original contract thoroughly, but Clober's post-audit modifications rendered their work meaningless.

 Like a horror movie victim who decides to investigate the strange noise alone, Clober walked right into one of crypto's most notorious traps.

 The story serves as a textbook example of how not to handle protocol security - deploy first, think later. 

 When will projects learn that audits aren't magical shields against their own rushed decisions? 

 Credit: Clober Dex , Nick Franklin , Peckshield , Kupia Security , Trust Security , Raz0r 
 Some thieves bring a crowbar, others just need a callback. 

 Some protocols still can't resist leaving their security checks unchecked.

 Clober Dex learned this the hard way when their Liquidity Vault bled $500k in yet another reentrancy exploit.

 While most of crypto slept, one attacker found their opening through a simple exploit.

 By the time anyone noticed, 133 ETH was already on the move. 

 Like clockwork, Clober's team rushed to Twitter with the familiar "URGENT: Security Breach Alert" playbook. 

 They assured users that while their Liquidity Vault had been compromised, the core protocol remained unscathed.

 Stop me if you've heard this one before - another reentrancy exploit making its rounds through DeFi.

 According to the breakdown provided by Nick Franklin , the attacker's recipe was depressingly simple: find the unguarded _burn function, abuse its burnHook callback, and watch the ETH flow.

 Using their own malicious token contract and a custom strategy, they orchestrated a dance of incomplete state updates and multiple withdrawals, waltzing away with 133 ETH. 

 Attack transaction: 0x8fcdfcded45100437ff94801090355f2f689941dca75de9a702e01670f361c04 

 Attacker Address: 
 0x012Fc6377F1c5CCF6e29967Bce52e3629AaA6025 

 The stolen funds didn't stay still for long.

 PeckShield tracked the attacker's movements as they bridged the 133 ETH from Base to Ethereum mainnet, splitting the spoils between two addresses.

 Stolen funds sent to: 

 0x711C87A0767101Fa6f3893FACb670B5689621e23 

 0x7760d838192f6E526721a0f6b160627baE989a3e 

 As fingers pointed and questions flew, attention turned to the protocol's security history. 

 The aftermath revealed a complex web of audit histories. 

 Trust Security, who had audited the original contract, were quick to distance themselves from the carnage :

 “A post-audit code change introducing the reentrancy attack was audited by another firm.”

 Trust Security Audit 

 Meanwhile, the other firm, Kupia Security found themselves caught in the crossfire after revealing they'd flagged potential issues with malicious strategies – though Clober insisted this was "NOT related to the reentrancy attack." 

 Adding another layer to the story, Kupia Security had completed their own audit just days before the exploit . 

 They had raised concerns about potential issues with malicious strategies in the Rebalancer contract, though Clober maintained these warnings were unrelated to the actual exploit.

 Kupia Security Audit 

 According to Raz0r from Decurity, the vulnerable burnHook call appeared to be a post-audit addition - a critical detail that might explain how such a well-known vulnerability slipped through the cracks.

 A familiar pattern emerged: different audit findings, post-audit changes, and somewhere in between, basic security practices slipped through the cracks.

 In the end, Clober did what every recently exploited protocol does - offered the attacker a 20% bounty and promised not to press charges. 

 But when protocols treat audits like checkboxes and deploy code without review, who's really to blame when the callbacks come home to roost? 

 Call them audits, reviews, or security checks - they mean nothing without proper deployment practices. 

 Projects rush to tout their security partnerships while quietly pushing unreviewed changes. 

 Each reentrancy exploit feels like a rerun, yet protocols keep falling for the same tricks.

 Trust Security and Kupia did their jobs, flagging issues and reviewing code.

 Yet somewhere between their reports and deployment, basic security measures vanished into thin air.

 The carnage that followed serves as another testament to crypto's goldfish memory when it comes to security.

 Maybe next time a protocol considers deploying unchecked code, they'll remember Clober's $500k lesson. 

 But with DeFi's track record, why wait for the next victim when we could just check the callbacks? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

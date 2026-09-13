# [H] Makina exploit: Makina Finance bled $4.13 million on January 20th through an oracle manipulation so textbook it could've been ripped from the Cantina CTF exclusion li

## Summary
Severity: High
Target: Makina
Loss: $4,130,000
Published: 1/20/2026
Source: https://rekt.news/makina-rekt
Type: rekt-postmortem

## Details
## Makina - Rekt

 Thursday, January 22, 2026 Makina - Oracle Manipulation - Rekt 

 read this article also in : 

 Six audits. One hundred million in TVL. Zero protection against the attack vector explicitly listed as out of scope. 

 Makina Finance bled $4.13 million on January 20th through an oracle manipulation so textbook it could've been ripped from the Cantina CTF exclusion list . 

 "Losses caused by oracle price/liquidity pool manipulation, where an unchecked synchronous deposit is used."

 That exact phrase sat in Cantina’s audit scope document while Dialectic, Makina's first Operator, deployed DUSD tokens into Curve pools with a share price mechanism that trusted spot prices like a tourist trusts a three-card monte dealer.

 Flash loan goes in, manipulated price gets locked, profit walks out - $280 million borrowed , pools drained, one atomic transaction, no TWAP, no delay, no second chance. 

 MEV bots front-ran the original attacker and grabbed most of the haul, splitting $4.13 million across two addresses while Makina sent polite on-chain messages offering a 10% bounty for funds that were already being laundered.

 ChainSecurity, OtterSec, SigmaPrime, Enigma Dark, Cantina - every firm signed off on "high level of security" while the protocol marketed itself as infrastructure where "every new protocol integration no longer requires new code, new audits, nor does it introduce new attack vectors."

 Turns out the attack vector was flexibility itself. 

 When auditors write the exploit in the out-of-scope section and nobody reads the fine print, who exactly failed the security review? 

 Credit: Peckshield , Cantina , CertiK , TenArmor , ExVul , Arkham , Makina , dewhales , n0b0dy , SlowMist , Defimon , QuillAudits , Blocksec Phalcon , DefiLlama , cyber.fund 
 January 19th - TenArmor's monitoring flagged suspicious activity on Makina Finance. 

 The attack happened on the DUSD/USDC CurveStable pool . 1299 ETH swept away (worth roughly $4.13 million at the time of the exploit).

 ExVul arrived shortly after with the diagnosis : "The lastTotalAum value is derived from Curve pool states which can be manipulated within a single atomic transaction via flash loans."

 CertiK confirmed shortly after : The majority was captured by an MEV builder address.

 But here's where it gets weird.

 Original attacker address ( according to Makina’s Incident Update ): 

 0x2F934B0Fd5c4f99BAb37d47604a3a1AEADEF1CCc 

 They deployed an unverified exploit contract in block 24273361. One block later , an MEV searcher ( 0x935bfb495E33f74d2E9735DF1DA66acE442ede48 ) decompiled the contract and replicated the attack for themselves.

 Two addresses. Two different operators. $3.3 million in one wallet, $880k in another . 

 PeckShield tracked it : 1,299 ETH total, split between two addresses: 
 0xbed26250Db2097318386F540fD546acEDf7bdE25 
 0x573Db3Aed219EfD4D2cDABC0D00366E7B80F910E ( Labeled Rocket Pool Node Distributor on Arkham )

 Makina's response wasn't a war room scramble - it was a negotiation .

 An onchain message was sent to one of the addresses involved in the MEV front running operation: 10% whitehat bounty if you return the funds. Keep up to 102.3 ETH, send back 920.7 ETH. 24-hour deadline.

 The message laid out the terms clearly: cooperate and keep the bounty, or face "judicial matter" escalation.

 Onchain message to the Attacker: 

 0xc5c5898eaf8c9ac7bee2c28eb971e8c5fee51c9ecdaf48b42c3357186c0235bf 

 Hypernative had actually caught an attack attempt one block before the main exploit. One block of warning. One block too late. 

 By the time Makina posted their incident update , the damage was contained but not reversed. 

 The Security Council triggered recovery mode , pausing all Machines in coordination with SEAL911 and their security auditors. Hypernative had caught the attack attempt one block before - but the actual exploit was carried out by the MEV bot that front-ran it.

 Isolated to DUSD/USDC Curve pool LPs . DUSD holders, Pendle positions, Gearbox integrations, other Machine tokens - all unaffected.

 Makina claimed leads on the MEV operators' identity and "strong reasons to believe they'll be cooperative."

 Dialectic, Makina's first Operator and strategic design partner, had moved DUSD into Curve pools in late October 2025 .

 Six weeks after Dialectic moved DUSD into Curve pools during Season 1's shift to active management , someone found the pricing mechanism and turned it into an ATM. 

 When your MEV bots become your biggest security problem and your whitehat bounty offer, did the exploit really fail or just get redistributed? 

## The Oracle That Trusted Everything

 Most oracle exploits require creative manipulation - reentrancy tricks, sandwich attacks, multi-block MEV schemes. 

 This one just asked the protocol to update its own accounting mid-transaction. 

 Makina's share price oracle - the mechanism that determines how much DUSD is worth - relied on a function called updateTotalAum().

 AUM. Assets Under Management. The total value of everything the Machine controls.

 Simple concept. Fatal implementation.

 updateTotalAum() was permissionless . Anyone could call it. Anytime. Mid-transaction. 

 It pulled data from calc_withdraw_one_coin() on Curve's MIM/3CRV pool - a function that estimates withdrawal amounts by checking whatever the pool balances happen to be at that exact moment. 

 Current pool state. Spot prices. The oracle has no time delay, no TWAP, no sanity check.

 The function would query the Curve pool, calculate what one coin was worth based on that exact moment's balances, lock that value into lastTotalAum , and update the share price accordingly.

 N0b0dy from CertiK explicitly states : "the price anchor is fully manipulable in the same transaction... the Curve pool pays out at the distorted rate."

 Same transaction. Same block. Same atomic execution.

 The code had no access control on updateTotalAum(), no time-weighted average pricing, no delay between price updates , no minimum time between calls, no comparison against previous values, no circuit breaker for abnormal movements - just a permissionless function pulling spot prices from pools that could be manipulated with borrowed capital.

 What it did have: Caliber's accountForPosition() function allowing pre-approved Weiroll commands, one of which was calc_withdraw_one_coin() - the exact function that could be manipulated with flash loan capital.

 The attack math becomes obvious once you see the architecture. 

 Step one: Flash loan the capital. Borrow 280 million USDC . Split between Morpho (160.6M) and Aave V2 (119.4M). 

 Capital doesn't need to be yours if you're only holding it for one transaction.

 Step two: Manipulate the Curve pools. Distort the pool balances across DUSD/USDC, 3pool, and MIM-3CRV.

 Dump 170 million USDC into the pools . Prices shift. Balances skew. The pools think DUSD is worth more than it actually is because the ratio just got hammered in one direction. 

 This isn't breaking the pools. It's using them exactly as designed - they respond to supply and demand, even if that demand is artificial and temporary. 

 Step three: Lock in the lie. Call accountForPosition() and updateTotalAum() .

 The function queries calc_withdraw_one_coin() on the manipulated pools .

 The manipulated pools spit back inflated values.

 lastTotalAum updates. getSharePrice() recalculates. 

 DUSD is suddenly worth more than it was five seconds ago. 

 Not because anything changed in the real world. Because the accounting said so. 

 Not because the code broke. Because the code worked exactly as written.

 Step four: Extract the value. Trade the remaining 110 million USDC into the ~$5 million DUSD/USDC pool.

 But the pool is paying out based on the inflated share price.

 Swap DUSD for USDC at the manipulated rate. Withdraw LP tokens at the inflated valuation.

 The pool hemorrhages 5,107,871 USDC . 

 Repay the flash loans. Keep approximately $4.13 million profit. 

 Convert to WETH on Uniswap V3. One transaction. One block. Pool drained.

 The entire sequence executed atomically. No pause. No delay.

 Phalcon's transaction trace shows it clearly : updateTotalAum() called before the DUSD-to-USDC swap and LP withdrawal (lines 1062 to 1067 ).

 The manipulated state became the accounting truth. The inflated price became the withdrawal reality.

 Multiple security firms confirmed the root cause: ExVul flagged "share price oracle manipulation via lastTotalAum," CertiK documented the "MachineShareOracle manipulated using 280M USDC flash loan," SlowMist traced "AUM pushed up through calc_withdraw_one_coin manipulation ," and Blocksec Phalcon identified "spot price calculation that allowed for an arbitrage attack ."

 The attack didn't break anything. The system worked exactly as designed - which was the problem.

 Just permissionless accounting updates pulling spot prices from pools that could be moved with borrowed capital. 

 When your oracle trusts the current block's state and anyone can update it mid-transaction, is it really an oracle or just a price-reporting service with delusions of security? 

## The Money Trail

 The attacker moved fast. But they were not alone. The blockchain kept receipts. 

 Every address. Every transaction. Every wei accounted for. 

 Primary Attack Transaction: 
 0x569733b8016ef9418f0b6bde8c14224d9e759e79301499908ecbcd956a0651f5 

 One transaction. Over $4 million drained.

 Original Attacker ( deployed exploit contract in block 24273361 ): 0x2F934B0Fd5c4f99BAb37d47604a3a1AEADEF1CCc 

 MEV Searcher ( decompiled and replicated attack in block 24273362 ): 0x935bfb495E33f74d2E9735DF1DA66acE442ede48 

 Attacker's Exploit Contract (Delegated execution): 0x454d03b2a1D52F5F7AabA8E352225335a1b724E8 

 This contract handled the heavy lifting - flash loan coordination, pool manipulation, AUM updates, withdrawals.

 Flash Loan Sources are as follows . 

 Morpho: 160,590,920,349,812 USDC
 Aave V2 Lending Pool: 119,409,079,650,188 USDC
 Total borrowed: 280 million USDC.

 Targeted Pool - DUSD/USDC Curve StableSwap: 

 0x32E616F4f17d43f9A5cd9Be0e294727187064cb3 

 Exploited Caliber Contract: 
 0x06147e073B854521c7B778280E7d7dBAfB2D4898 

 The contract that exposed accountForPosition() with pre-approved Weiroll commands including calc_withdraw_one_coin(). 

 But here's where the story splits into something stranger. 

 The original attacker set up the exploit. Deployed an unverified contract.

 Before they could execute, an MEV searcher decompiled the contract, replicated the attack logic, and beat them to the punch by one block.

 MEV Builder Address: 
 0xa6c248384C5DDd934B83D0926D2E2A1dDF008387 

 This address intercepted the transaction, reordered the execution, and captured the majority of the profit. 

 The stolen funds didn't go to the original hacker. They went to two addresses that Makina believes are non-malicious MEV operators . 

 MEV Recipient Address 1: 
 0xbed26250Db2097318386F540fD546acEDf7bdE25 

 Holdings: 1,062 ETH (~$3.3M)

 MEV Recipient Address 2: Rocket Pool Node Distributor (received 276 ETH from the exploit): 0x573Db3Aed219EfD4D2cDABC0D00366E7B80F910E 

 Rocket Pool Validator Owner Address (identified, not yet contacted): 

 0x3b6fc5cc2feefc357212617930aedac9493288af 

 Holdings: 276 ETH (~$880K)

 Total captured by MEV: 1,299 ETH (~$4.13M)

 Fund Movement Transaction (to MEV Address 1): 
 0x14d2725f4cac331740b053ae49176cec780b556e4aacc3a9f70d77644e97a2a7 

 Makina didn't threaten. They negotiated.

 Makina's On-Chain Message Transaction 1: 

 0xc5c5898eaf8c9ac7bee2c28eb971e8c5fee51c9ecdaf48b42c3357186c0235bf 

 Makina's On-Chain Message Transaction 2: 
 0xfe12d36617e2d1d6ab43716159ad7737606837fe9ea0cb781054f6f3c4fea52f 

 Sent to both MEV addresses. Polite. Professional. Offering 10% bounty: 

 "The 1,023 ETH you received has come from a smart contract exploit. We do not believe this was intentional on your part. Return 920.7 ETH, keep 102.3 ETH as whitehat bounty." 

 Recovery Wallet: 
 0x62244C74e1d09b3D86EF7342d354b5D7770bDE10 

 A 24-hour deadline, which has since expired with no response.

 But recovery efforts are underway : 

 Makina is working to recover ~1,023 ETH from the MEV builder. Outreach efforts to identify the owner of Rocket Pool validator (0x3b6fc...). Dialectic is transferring $104,491 in LP fees inadvertently earned during the exploit back to affected users. They are targeting Monday, January 26th to reactivate redemptions after patch audit completes. They’re also deprecating the DUSD/USDC Curve pool entirely and moving to Uniswap.

 Meanwhile, the original attacker's address? Empty. Front-run before they could collect a single wei. Bet they thought they were about to score, but MEV operators said otherwise. 

 When the MEV bots steal from the thieves and the protocol negotiates with the bots instead of the original hacker, who exactly is the victim and who's the accomplice? 

## Six Audits, One Blindspot

 Makina's security resume wasn't thin. 

 Six audits. Five different firms. Five months of scrutiny. 

 Enigma Dark : Makina-Core Fuzz/Invariant Testing (July 2025)

 SigmaPrime : Makina-Core & Makina-Periphery (August 2025)

 ChainSecurity : Makina-Core (September 2025)

 ChainSecurity : Makina-Periphery (September 2025)

 Cantina : CTF Competition (September 18 - October 15, 2025)

 OtterSec : Makina-Core & Makina-Periphery (November 2025)

 Everything audited. Everything passed. Everything except the thing that mattered. 

 Cantina's CTF competition : A live bug bounty where hackers attack real contracts for cash prizes - ran from September 18 to October 15, 2025.

 Participants could exploit anything they found. Keep the funds if the exploit was valid.

 Except for a list of explicitly excluded attack vectors.

 From the Cantina scope document : 

 "Losses caused by oracle price/liquidity pool manipulation, where an unchecked synchronous deposit is used." 

 "Any loss of funds or share price inconsistency caused by faulty instructions." 

 That first line. Word for word. The exact attack that drained $4.13 million three months later. 

 Not a warning buried in the appendix. Listed front and center in the out-of-scope section.

 The auditors drew a circle around the attack vector, labeled it 'out of scope,' and moved on.

 July-November 2025 : Core infrastructure audited and approved

 September 29, 2025 : Season 0 launches. DUSD, DETH, DBIT go live.

 October 15, 2025 : Cantina CTF ends. Oracle manipulation explicitly excluded from scope.

 October 27, 2025 : Season 1 begins. Dialectic transitions from passive Morpho lending to active management.

 Post-October 2025: DUSD deployed into Curve pools . Share price oracle goes live pulling spot prices with zero delays. Permissionless AUM , no TWAP, no access control , oracle manipulation sitting in production, six weeks from detonation.

 January 19, 2026 : Exploit occurs.

 The vulnerability wasn't in the audited code. 

 It was in the integration deployed after the audits finished. 

 Responsibility gets murky when you trace the vulnerability.

 Makina designed the system. Built the MachineShareOracle. Created updateTotalAum() as a permissionless function. Allowed Operators to deploy arbitrary strategies with pre-approved Weiroll commands .

 One of those pre-approved commands was part of the exploit: calc_withdraw_one_coin() on Curve pools .

 Dialectic, the Operator and Makina's strategic design partner, chose which pools to deploy into and manages the strategy through their risk framework . 

 The accountForPosition() function in Caliber ? Makina's code. 

 The pre-approved Weiroll commands? Included calc_withdraw_one_coin() on Curve pools .

 The oracle? No time delay, no TWAP, no access control. 

 Makina was described by investors as infrastructure where: "Every new protocol integration no longer requires new code, new audits, nor does it introduce new attack vectors."

 Flexibility was the selling point. Deploy to any protocol. No custom adapters. No waiting for audits. 

 That flexibility became the attack surface. 

 $100 million TVL at time of the exploit.

 The damage was contained. The warning signs weren't.

 Cantina listed oracle manipulation as out of scope in their CTF. The Curve pool integration was deployed after that CTF ended.

 The exploit used the exact attack vector Cantina had excluded from examination. 

 When auditors explicitly exclude the attack vector that eventually drains your protocol, then call it "out of scope" instead of "unacceptable risk," are they protecting themselves or warning you? 

 Six audits couldn't stop what nobody asked them to examine. 

 Makina built a flexible execution engine marketed on the premise that new integrations wouldn't introduce new attack vectors, then got drained through an integration deployed after every audit signed off. 

 The Cantina CTF literally listed oracle manipulation via spot prices as out of scope - not because it wasn't a risk, but because nobody wanted responsibility for it.

 The audits did their job. They verified the code worked as written. They confirmed the core contracts were secure.

 What they didn't do - what they explicitly avoided doing - was question whether the design itself was fundamentally unsafe.

 When your security model depends on assuming external price feeds won't be manipulated within the same transaction, you're not building institutional-grade infrastructure. You're building an honor system with bytecode. 

 Dialectic, one of DeFi's most respected asset managers, chose the pools. Makina built the oracle. 

 The vulnerability lived in the space between them - deployed live, processing $100 million in TVL, three months after the last auditor closed their report.

 The funds remain frozen while Makina works contacts at MEV infrastructure providers, hoping that whoever front-ran the original attacker decides cooperation beats keeping the money.

 Flexibility was marketed as safe.

 Auditors wrote "not our problem" next to the exact attack that succeeded.

 MEV bots front-ran the exploit and captured most of the funds while the protocol scrambled to respond. 

 Did we build the future of finance, or just a faster arena where automation beats human response time and the quickest code wins regardless of intent? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

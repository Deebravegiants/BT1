# [C] THORChain - Rekt III exploit: The relationship between THORChain and North Korea runs deeper than most protocols would care to admit

## Summary
Severity: Critical
Target: THORChain - Rekt III
Loss: $10,700,000
Published: 5/15/2026
Source: https://rekt.news/thorchain-rekt3
Type: rekt-postmortem

## Details
## THORChain - Rekt III

 Thursday, May 21, 2026 THORChain - Rekt 

 read this article also in : 

 Three exploits in five years . Toss in a $200 million insolvency crisis . Sprinkle $1.2 billion in North Korean laundering on top. 

 The relationship between THORChain and North Korea runs deeper than most protocols would care to admit. 

 North Korea even returned the favor, draining $1.2 million from co-founder jpthor's personal wallet in September 2025 via a fake meeting scam.

 Not exactly a recipe for success, but rather disaster.

 Then on the morning of May 15th, another $10.7 million was stolen.

 At some point, the question stops being how did this happen, and starts being why anyone expected otherwise? 

 On May 15, 2026, THORChain's Asgard vault was drained across multiple chains in rapid succession. 

 THORChain's own auto-solvency checker fired the halt - the one security upgrade born out of the July 2021 carnage - and froze the network for twelve hours and forty-two minutes.

 The vault held. The funds did not.

 RUNE dropped 15% before most of the world had finished reading ZachXBT's Telegram post.

 Market cap shed $27 million in minutes.

 This is a protocol that has stared into the abyss before and kept building. But there is a limit to how many times you can call the same wound a learning experience. 

 When the vulnerability class was documented, the patches existed, and the funds are gone anyway, at what point does deferred maintenance become negligence? 

 Credit: DBCrypto , CCN , CoinDesk , ZachXBT , Amb Crypto , CryptoTimes , TRM Labs , THORSwap , banteg , THORChain , Fireblocks , verichains , Charles Guillemet , Tayvano , jpthor , QuillAudits , Chainalysis , ImmuneFi , Luke Parker , Trail of Bits , Halborn , crypto.news 
 ZachXBT saw it first . 

 Early on May 15, his Telegram channel posted a community alert : THORChain was likely exploited on Bitcoin, Ethereum, BSC, Base for $10.7M+.

 TRM Labs would later expand the confirmed scope to at least nine chains - adding Avalanche, Dogecoin, Litecoin, Bitcoin Cash, and XRP to the initial four - and revise total losses upward past $11 million.

 Arkham labeled the exploiter wallet.

 But, the drain was already done. 

 PeckShield confirmed it publicly : ~$10M drained, including 36.75 BTC and roughly $7M in assets across BNB Chain, Ethereum, and Base. 

 THORChain's own infrastructure moved before the team did.

 THORChain's Mimir governance module flipped trading halt and signing halt parameters to active, with a node pause running for approximately 12 hours and 42 minutes from block 26190429 .

 No human had to make the call.

 Over 5 hours after ZachXBT’s announcement , THORChain posted an official statement confirming what on-chain data had already made plain : One of six Asgard vaults had been compromised. $10.7 million gone. 

 Node operators securing the affected vault had their bonded RUNE slashed as a consequence of the unauthorized outbound transactions. Churn paused. Chain onboarding delayed indefinitely. Initial indications show no individual user swaps were affected. 

 THORSwap and Metro.exchange halted THORChain routing immediately. 

 Maya Protocol paused out of precaution.

 ATOM trading went dark.

 Alternative providers - Chainflip, NEAR Intents, Harbor, Flashnet, Garden, 1inch - kept running, unaffected . 

 While the ecosystem scrambled, the on-chain record was already telling a different story. 

 Among the earliest signals pointing toward the why: banteg flagged a GitLab commit to THORNode , authored May 6 - nine days before the exploit - titled "sign full ObservedTx wrapper to prevent proposer forgery." 

 A patch existed. It had a name and a timestamp. It had never shipped.

 The commit would prove to be one thread in a larger fabric of deferred maintenance, not the root cause, but an early indicator of the gap between what was known and what was acted on. 

 Nine days separated a committed patch from a $10.7 million loss - so who, exactly, is responsible for what lives in that gap? 

## One Node, One Key, One Sweep

 THORChain's vaults are secured by Threshold Signature Scheme, TSS, a form of Multi-Party Computation where a quorum of nodes jointly produce a cryptographic signature without any single node ever holding the complete private key. 

 On paper, distributed trust. In practice, only as strong as every co-signer in the quorum. 

 The setup started weeks before the drain. A freshly created Discord handle - "Dinosauruss" - joined the THORChain Developer Discord on May 1 , asking questions about how to get a node churned into the network as quickly as possible.

 The normal three-day churn interval was delayed due to unrelated reasons , forcing the attacker to wait. On May 13, two days before the exploit, a brand-new node operator with approximately 635,000 RUNE across two bond addresses churned into the active validator set and was randomly assigned to one of the five vaults.

 Over the following two days , the node participated in routine GG20 signing ceremonies, getting everything it needed.

 THORChain's confirmed finding : The attacker exploited a vulnerability in the GG20 TSS implementation that allowed sensitive key material from vault participants to leak over time. 

 By accumulating enough leaked material across signing rounds , the attacker reconstructed the vault's full TSS private key and executed unauthorized outbound transactions directly. 

 The proactive solvency checker checks for insolvency before signing. There was no signing to catch. The reactive checker fired when the vault came up short , by then the funds were already gone.

 The solvency checker functioned as designed. The attack simply went around the layer it monitors .

 To understand why the attacker could reconstruct the key in the first place, you have to understand what THORChain was running.

 GG20 is a widely used protocol for threshold ECDSA , which is commonly used in systems that interact with Bitcoin and Ethereum. 

 It also has a documented history of critical vulnerabilities. 

 CVE-2023-33241 and TSSHOCK , both disclosed in 2023, are key extraction attacks requiring only one compromised co-signer to reconstruct the full private key - silently, without triggering an abort, leaving no trace in normal protocol operation.

 The specific mechanism used against THORChain has not been publicly confirmed to match either CVE, but both illustrate the class of attack the library is vulnerable to.

 THORChain's TSS runs on a fork of Binance's tss-lib implementing GG20.

 That fork, as Taylor Monahan noted shortly after the exploit was flagged : "Oh dear it appears THORChain was running tss-lib that was like 3 years and 2+ major security releases behind." 

 banteg published the most detailed technical analysis the day after the exploit , examining THORChain's deployed fork directly, tss-lib v0.1.6 at commit 287e1e2, as used by thornode v3.18.0. 

 His finding : The key-generation path accepts and persists peer Paillier material without the MOD/FAC proof family that establishes a well-formed two-prime Paillier modulus.

 A malicious node could therefore register a 2048-bit Paillier modulus that passes every check the library performs while containing attacker-known factors.

 Once that malformed key is persisted by honest nodes , every signing round that touches it exposes the oracle shape in the examined code, leaking residues of other participants' long-term signing shares that an attacker could accumulate and combine offline.

 His harness tests confirmed the oracle shape in the examined code. 

 jpthor had called this early , flagging GG20 as the most likely explanation within hours of the halt. 

 Charles Guillemet framed the broader structural problem : In every published GG18 and GG20 attack, one malicious or compromised co-signer is enough.

 Not a majority, not a quorum, one.

 The whole premise of distributed key security collapses at the co-signer layer if a single participant is malicious.

 jpthor has since laid out a three-step roadmap : Patch GG20 to get THORChain back online; migrate all ECDSA protocols to DKLS; then migrate Bitcoin signing to FROST. 

 His framing of GG20 as a "black box" with "many brittle assumptions" that will "forever be a bit of a black box" is as close to an internal admission as exists in the public record. 

 THORChain had engaged Silence Labs in November 2025 to build a custom DKLS implementation with a targeted delivery of Q1/Q2 2026, the reason GG20 was still in production at the time of the exploit. That work hadn't landed.

 THORChain's churning mechanism , the process by which validators rotate in and out of active Asgard vaults on a regular schedule, is what made this possible.

 Without it, there is no path for a malicious operator to join a vault, participate in signing ceremonies, and accumulate key material. The attacker didn't need to break the cryptography. They just needed to get inside the room.

 The investigation continues alongside THORSec and Outrider Analytics. 

 Law enforcement has been contacted. The attacker's identity remains unknown. 

 An exploit report was published on May 20th . A follow-up report will be issued once the investigation is complete and the recovery plan has been finalized.

 What is known is the node address, the on-chain links between bonding wallets and receiving wallets , and the confirmed mechanism - a cryptographic library years out of date, running on a fork that contained an implementation flaw capable of leaking vault key material to a single patient, malicious operator.

 Malicious Node: 
 thor16ucjv3v695mq283me7esh0wdhajjalengcn84q 

 THORChain's churning mechanism exists to rotate trust, someone used it to buy time instead. 

 So how many other GG20-based vaults across DeFi are sitting on the same unpatched library, waiting for the next patient operator? 

## Swept Clean

 Multiple chains, dozens of tokens, one address. 

 Whoever did this knew exactly where everything was and moved with a precision that doesn't suggest improvisation. 

 Every ERC-20 token across Ethereum, BNB Chain, and Base was funneled into attacker-controlled addresses before the network halt had fully propagated. The Bitcoin moved in parallel.

 By the time ZachXBT posted his alert , the consolidation was already complete.

 QuillAudits published a full chain-by-chain breakdown on May 19.

 The drain broke down as follows… 

 Malicious Actions on Ethereum 

 Stablecoins, blue-chip DeFi tokens, and protocol-native assets drained from the vault : 

 1,756,756.02 USDT · 1,261,986.53 USDC · 73,768,463.86 XRUNE · 3,349,323.54 THOR · 5.206 WBTC · 64,138.47 LUSD · 61,074.86 GUSD · 38,762.45 USDP · 1,044.06 LINK · 4,567.54 DAI · 78.10 AAVE · 1,514.92 SNX · 481,996.68 FOX · 1.057 YFI · 11.43 DPI 

 Attacker Address: 

 0x82fc0d5150f3548027e971ec04c065f3c93154eb 

 THORChain Vault: 

 0x82a5CF67F3e6970C0529122178075C0a94878bDA 

 Transfer Out Transactions: 

 View all on Etherscan 

 Funds were sent here (~$6.77 Million): 

 0xd477b69551f49C0519F9B18c55030676138890Bd 

 Malicious Actions on BNB 

 A diverse basket of tokens including stablecoins , wrapped BTC, and ETH equivalents were drained: 

 274,256.09 USDC · 125,117.17 BSC-USD · 32,144.23 BUSD · 32,980.44 TWT · 15.615 ETH · 0.509 BTCB 

 Attacker Address: 

 0x82fc0d5150f3548027e971ec04c065f3c93154eb 

 THORChain Vault: 

 0x82a5cf67f3e6970c0529122178075c0a94878bda 

 Transfer Out Transactions: 
 View all on BSCscan 

 Malicious Actions on Bitcoin 

 Two outbound transactions totaling over 40 BTC (~$3.26M) : 

 36.85351435 BTC · 3.87429558 BTC 

 Attacker Address: 

 bc1ql4u94klk265lnfur2ujk9p6uh52f2a8jhf6f37 

 THORChain Vault: 

 bc1qt8f467qdkpmuflgwvgvvlr86r0kldnnvm7zhyv 

 Transfer Out Transactions: 

 View all on mempool.space (scroll down to transactions)

 Malicious Actions on Avalanche 

 Avalanche stablecoins and SOL equivalent assets drained : 

 238,325.94 USDC · 43,041.25 USDT · 388.94 SOL 

 Attacker Address: 

 0xd477b69551f49C0519F9B18c55030676138890Bd 

 THORChain Vault: 

 0x82A3580296b014c27cFe6be23Ed471c30D878Bda 

 Transfer Out Transactions: 

 0xd477b69551f49C0519F9B18c55030676138890Bd 

 Malicious Actions on Base 

 USDC drained in a single outbound transaction : 

 55,912.41 USDC 

 Attacker Address: 

 0xd477b69551f49C0519F9B18c55030676138890Bd 

 THORChain Vault: 

 0x82a5cf67f3e6970c0529122178075c0a94878bda 

 Single Drain Transaction: 0x4370739cf3f443fe129727ea1a9e215783d881c643f3ea1d12ce822aeb3e6af8 

 Malicious Actions on Dogecoin 

 Nearly 7.82M DOGE drained across two near-identical outbound transactions (~$900K) : 

 3,911,749.91 DOGE · 3,911,751.03 DOGE 

 Attacker Address: 

 DBLJWFemMHbduKofBRg6TJ9XFAgWdvFCjS 

 THORChain Vault: 

 DDL3tEh5P5vjSCNyU7t7sz9DQykRnr97d2 

 Transfer Out Transactions: 
 View on BlockChair 

 Malicious Actions on Litecoin 

 LTC drained from the vault : 

 6,866.74772083 LTC 

 Attacker Address: 

 ltc1qg0h4rz5kf27fkr99gamw4heg20rfz5epd7m7wh 

 THORChain Vault: 

 ltc1qt8f467qdkpmuflgwvgvvlr86r0kldnnvlzcnuu 

 Single Drain Transaction: 
 F5985741ef6d7418cd2f0f4e909b6f0d525f18c6010cca48d846731f23972bd4 

 Malicious Actions on Bitcoin Cash 

 BCH moved out of the vault in a single transaction : 

 638.52948245 BCH 

 Attacker Address: 

 qpp775v2je9texcv54rhd6kl9pfudy2nyyz4df2uvc 

 THORChain Vault: 

 qpvaxhtcpkc8038ape3p3nuvlgd7makwds74qyng5p 

 Transfer Out Transactions: 

 View on Blockchain 

 Malicious Actions on XRP 

 XRP drained across two transactions : 

 25,404.922305 XRP · 16.999982 XRP 

 Attacker Address: 

 rwoGBrYEJ28jhBjchrTyCGXd1Pt4pobFBz 

 THORChain Vault: 

 r9BxLykSngpSuUU4jXtZLDycXip3Suo7Rf 

 Transfer Out Transactions: 

 View on XRPScan 

 Malicious Actions on TRON 

 89,172 TRX swapped to 31,215 USDT via SunSwap, bridged to Ethereum - 13.9 ETH delivered to the known ETH laundering hub. 

 TRON signing, trading, and solvency checks halted and disabled in Mimir , matching the pattern of the confirmed drained chains.

 Attacker Address: 

 TXmo5sdVCvQnJgbvjAUpQJfyNx5EnqtAM3 

 THORChain Vault: 
 TMt1UgzBNKETQMgGckJDomcMQhvwhGUiXo 

 TRON Drain Transaction: 

 0ee50dd1af24c08a2f73fab18dd96897fcd6c08cfca0a6397b519c8fe1fdf1f4 

 ETH Delivery: 

 0x09c4bc73fddaac5697a609cb448cefc26e13ccba22ce1b762b309b010e0db5f4 

 Funds sent to Ethereum Address: 

 0x82fc0d5150f3548027e971ec04c065f3c93154eb 

 THORChain's official statement confirmed that node operators securing the compromised vault had their bonded RUNE slashed as a direct consequence of the unauthorized outbound transactions. 

 Protocol-owned funds were lost. Per the team's initial assessment, no individual user swaps were affected. The slashing mechanism worked. The vault did not. 

 The exploit looked sudden, but it wasn't.

 Chainalysis published a five-part thread on May 15 , mapped weeks of preparatory activity beginning in late April - the attacker funding the entry through Monero, bonding RUNE for the node that became the attack vector , and delivering 8 ETH to the final receiving wallet just 43 minutes before the drain .

 Multiple chains. One patient operator. Three weeks of preparation. The network halted itself the moment something looked wrong. By then, the attacker was done. 

 What does it mean when the best thing about your security is how quickly it confirms the damage? 

## Audited, Just Not There

 THORChain has auditors. 

 It launched a bug bounty program with ImmuneFi after the 2021 exploits , later departing ImmuneFi under disputed circumstances in favor of a self-hosted program, which was itself retired in March 2026 , two months before the exploit. 

 It has a history of taking security seriously enough to hire both Halborn and Trail of Bits after the 2021 carnage, completing a five-pronged recovery plan that included red-teaming, protocol hardening, and formal audit sign-off before relaunching.

 None of that is in question. What is in question is where the audits were pointed.

 After the 2021 exploits, Trail of Bits conducted a full code audit of THORChain's core protocol - THORNode, the Bifrost bridge code, and crucially, the tss-lib implementation underpinning the TSS vault system.

 Halborn ran a separate penetration testing engagement covering the THORNode stack, Bifrost, and vault security - including a review of the threshold multisig implementation. 

 Both returned passing grades. No unresolved critical vulnerabilities at time of issuance. 

 In December 2021, Trail of Bits went further, disclosing Shamir's Secret Sharing vulnerabilities in tss-lib that affected THORChain directly.

 THORChain patched it. The protocol relaunched. The audits aged.

 Since then, Halborn has remained active, conducting eight separate security assessments between January and November 2025.

 Every single one was scoped to Rujira , THORChain's smart contract application layer: Lending contracts, order book DEX, staking modules, lending pools. 

 Useful work. Necessary work. Work that had nothing to do with the layer that just lost $10.7 million. 

 2020 - Early Security Work: 

 CertiK · Apr 2020 · THORChain code review 

 Kudelski Security · Jun 2020 · THORChain TSS 

 IOActive · Nov 2020 · penetration test 

 2021 - Core Protocol: 

 Trail of Bits · Aug 2021 · THORChain core + tss-lib 

 Halborn · Sep 2021 · TSS audit 

 Halborn · Sep 2021 · State machine, Router + Bifrost 

 Trail of Bits · Dec 2021 · tss-lib Shamir's Secret Sharing - vulnerability disclosure (patched) 

 2024/2025 -Bifrost observation layer: 

 Zellic · Nov 2024 · THORChain Bifrost 

 Zellic · Jan 2025 · THORChain Bifrost UTXO Client 

 2025 - Rujira application layer only: 

 Halborn · Jan-Feb 2025 · Rujira Trade (FIN) smart contracts 

 Halborn · Feb 2025 · Rujira Pools (BOW) smart contracts 

 Halborn · Mar-Apr 2025 · Rujira Staking smart contracts 

 Halborn · May 2025 · NAMI Protocol Rujira Index Product 

 Halborn · Aug 2025 · CALC Manager/Scheduler/Strategy smart contracts 

 Halborn · Oct 2025 · Ghost Vault (RUJI Lending) smart contracts 

 Halborn · Oct-Nov 2025 · Ghost Credit (Credit Accounts) smart contracts 

 Halborn · Nov 2025 · Rujira Trade FIN v1.1 smart contracts 

 The GG20 tss-lib fork specifically, the cryptographic implementation at the center of this exploit, has not had a documented audit since 2021 . The broader THORChain codebase has seen more recent attention, but none of it touched this layer.

 Bifrost received more recent attention, with Zellic auditing the observation layer and a Code4rena contest in 2024 covering the EVM smart contract parsing logic . 

 But the cryptographic library at the center of this exploit, which Taylor Monahan noted was running years behind on security releases ,last saw formal review before the critical vulnerabilities in that codebase were publicly known. 

 None of the 2025 assessments touched it.

 TSSHOCK and CVE-2023-33241 , the two major GG20 vulnerabilities, were both disclosed in 2023.

 The Trail of Bits audit that covered tss-lib predates both disclosures. 

 The protocol kept running on the same library, through two publicized critical bugs, without a documented re-audit of that specific component. 

 To be clear: Audits are point-in-time assessments. They prove what they're asked to prove, within the scope they're given, at the moment they're conducted.

 Halborn didn't miss the GG20 vulnerabilities in 2021, those vulnerabilities weren't public yet.

 What's harder to explain is the absence of any follow-up audit of the core protocol layer after they were.

 Eight audits in 2025, all pointed at the application layer, and the cryptographic foundation holding the vaults hadn't been formally reviewed since before the vulnerabilities in it were publicly known. 

 Who decided that was an acceptable posture? 

 THORChain has survived everything. 

 Two exploits in ten days in 2021. A $200 million insolvency crisis that looked, briefly, like a death spiral. $1.2 billion in North Korean laundering that split its own community in half and drove out core contributors. 

 It absorbed every hit, restructured, kept the DEX running, and called it resilience.

 What it never fully absorbed was the lesson underneath each one.

 The cryptographic library securing the vaults was years behind on security releases . 

 The last audit of the core protocol predates the public disclosure of the vulnerabilities now under investigation. 

 And yet eight audits shipped in 2025, every one of them pointed somewhere else.

 Shortly after the exploit, fake refund portals were circulating , scammers targeting the same users who had just watched their funds disappear.

 By May 18, THORChain was forced to issue an explicit public warning : There is no refund portal. Please rely only on official channels. 

 That warning remains live on the top banner of THORChain's own website. 

 A protocol that lost $10.7 million to a patient, sophisticated attacker spent the following day fighting off opportunists harvesting its own victims.

 The investigation continues alongside THORSec and Outrider Analytics , with law enforcement engaged.

 An initial exploit report was published on May 20. A follow-up report is pending. No compensation plan exists so far.

 The governance vote on how to handle losses, ADR-028, has not yet concluded .

 No timeline has been given for a full network restart. 

 The protocol that laundered $1.2 billion for North Korea earned at least $12 million in fees from it , a conservative estimate per Chainalysis , and called that neutrality. 

 Node operators initially voted to halt ETH trading when Lazarus came through. The vote was reversed within minutes .

 A core contributor resigned. The network kept running.

 Then on May 15, THORChain's own vault was drained, and the same protocol that found a philosophical reason not to halt for Lazarus found a technical one to halt itself in twelve hours and forty-two minutes.

 That contrast hasn't gone unnoticed. 

 The question being asked loudly across the ecosystem : If THORChain has an emergency shutdown capability, why has it historically been deployed only when the protocol's own assets are at risk, and not when it was processing hundreds of millions in stolen funds for state-sponsored hackers? 

 Whether that reflects a genuine architectural distinction or a selective application of decentralization principles is a conversation THORChain can no longer defer.

 THORChain will likely survive this too. It has before, against longer odds.

 But survival and accountability are different things, and so far this protocol has been far better at the first than the second.

 THORChain halted for North Korea when it had no choice. It will rebuild from this because it always does. 

 But at what point does resilience stop being a virtue and start being an excuse? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

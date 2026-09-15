# [C] Ostium exploit: The attacker didn't touch a smart contract bug

## Summary
Severity: Critical
Target: Ostium
Loss: $23,750,000
Published: 7/15/2026
Source: https://rekt.news/ostium-rekt
Type: rekt-postmortem

## Details
## Ostium - Rekt

 Tuesday, July 21, 2026 Ostium - Price Feed Compromise - Arbitrum 

 read this article also in : 

 Five minutes and twenty-nine seconds. That's how long it took an Arbitrum perpetuals exchange backed by General Catalyst and Jump Crypto, and a fresh Nasdaq data partnership to lose $23.75 million . 

 The attacker didn't touch a smart contract bug. He walked in through Ostium's own price-reporting machinery and told the vault whatever price he wanted , whenever he wanted it. 

 Bitcoin opened at $5,000 . In the same breath, it closed at $60,000 . Nobody's portfolio moved twelvefold that afternoon. Only Ostium's vault did.

 The attacker looped leveraged trades against the vault until it was dry , and a five-minute window later, the OLP vault liquidity providers built to collect yield had instead financed a payout on trades that were never real, right down to the last cent.

 The component the attacker used wasn't a gap nobody noticed. It was a gap Ostium had written down, in its own bug bounty scope , as a place security researchers weren't allowed to look.

 Stolen funds hit Kyber within the hour, and Tornado Cash by nightfall , laundered faster than most of the security firms could agree on a dollar figure. 

 When the door you left unlocked is the one you told everyone not to check, is it still a break-in? 

 Credit: The Block , Rogue Trader , Blockaid , defiprime , QuillAudits , kaledora , ImmuneFi , Peckshield , Cyvers , Ostium , CBB , Lookonchain , CoinTelegraph , evm codes , Zellic , ThreeSigma , Pashov Audit Group , DefiLlama 
 Blockaid's detection system caught it mid-drain on July 15th , tagging the exploit transaction and the attacker's wallet before the last loop had even fired: "An attacker used a registered PriceUpKeep forwarder and future-dated authorized oracle reports to create artificial trade profit, triggering a ~$18M USDC payout from the vault." 

 RogueTrader had a bigger number within minutes , $23.75 million, and the exact attacker address to go with it. 

 Cyvers followed with the fullest picture yet: funds routed through ChangeNOW on Ethereum , bridged to Arbitrum, swapped entirely from USDC to ETH, and scattered across attacker-controlled wallets.

 Ostium showed up with their first announcement shortly after Blockaid’s initial alarm: “We are aware of the issue with the OLP vault. We have paused all trading. The team is investigating.”

 Ostium followed up with a post just over an hour and a half later : "Trading remains paused following the security incident. User positions remain open and unmodifiable, and trader margin remains unmoved in frozen trading smart contracts. Over the past 14 hours, the team has been in continuous coordination with relevant authorities, SEAL 911, and multiple security researchers."

 Ostium's founder, kaledora, acknowledged the incident that afternoon : "This morning, between 14:18-14:23 UTC, Ostium experienced a security issue leading to a loss of funds from the public OLP vault. Our team identified the issue within minutes and immediately began taking steps to contain it, including coordinating to pause trading contracts within the hour."

 Not everyone watching was sympathetic. CBB summed up the mood better than any security firm did : "Maybe next time focus on securing your protocol instead of trying to beef with Hyperliquid."

 QuillAudits published the first real technical trace , the attacker opening a leveraged trade, triggering a price upkeep call in the same transaction, the submitted report's signature recovering to an address the contract itself trusted, isAuthorizedSigner[recovered signer] == true.

 By the time PeckShield and Lookonchain finished tracing the exit, the full amount had already been swapped to 12,084 ETH and was moving into Tornado Cash . The forensic community had reconstructed the entire attack before Ostium had confirmed a single dollar figure. 

 If outside analysts can map your exploit down to the recovered signer address faster than you can post an update, what exactly does "investigating" mean? 

## Authorized to Lie

 Ostium can't read a Bitcoin price off a DEX pool the way a crypto-native perp can. 

 Gold, forex, the S&P, none of it exists on-chain. 

 So Ostium built a pull oracle instead : Prices are only written onchain when explicitly required for trade execution, delivered on demand by Gelato , the automation network Ostium's own docs describe as the only address authorized to trigger these actions.

 Ostium's own audit scope lists two price-upkeep contracts : PriceUpKeep and PrivatePriceUpKeep.

 That distinction matters for anyone trying to verify the exploit against Ostium's own contract list.

 In early coverage, the exploited contract was often referred to simply as “PriceUpKeep,” a convenient shorthand for the upkeep family rather than a specific deployment. 

 On-chain, the specific deployment matters. 

 Pulling the raw event logs from the main exploit transaction shows address 0xB71ec9eBD8145daCaCF6724363143cb5667A3d36 firing a PriceRequestedV2 event, tagged directly by Arbiscan's contract label as " Ostium: Private Price Up Keep ."

 The executeBatch calldata in the main exploit transaction backs it up: The internal calls repeatedly route between Ostium’s Trading contract and that exact address.

 The public PriceUpKeep contract , Ostium's other listed deployment, never appears anywhere in the transaction.

 Its recent activity had already stalled before the exploit, with the latest transactions showing repeated Perform Upkeep calls that revert with NotInitiated . 

 The contract used in the exploit path was PrivatePriceUpKeep , not PriceUpKeep , and they are separate deployments with separate histories . 

 In practice, that contract is the core of the model : It writes the signed price a trade settles at, right when the trade needs it. Trust the signer, trust the price. There is no second opinion.

 The internal trace shows PrivatePriceUpKeep calling into the verification path , which then makes a staticcall to the EVM's ecrecover precompile , showing that the exploit path relied on signature verification at that point .

 Ostium's own Registry contract, the reference every other contract in this system queries at runtime, shows the ostiumVerifier key was originally registered to a different address roughly 688 days before the exploit , then updated on February 14, 2026 , 151 days before the exploit, to the address that appears in the live trace.

 That same governance transaction also added four authorized signers to the new verifier, including the address flagged in QuillAudits' trace , showing that address was part of Ostium's approved signer set from the outset. 

 That registry update is consistent with what the live trace shows ; Ostium's public docs table and Arbiscan's "Verifier" name tag both appear stale relative to it, still pointing at the pre-update address . 

 The exploit path appears to have relied on two things: A registered PrivatePriceUpKeep forwarder capable of triggering its own price delivery, and a price report that passed the contract’s signature check, with QuillAudits tracing that signer to this address .

 Not a forged signature. Not a broken function. A report the protocol accepted as valid.

 A single executeBatch call produced twenty internal calls , alternating between Ostium's Trading contract and the PrivatePriceUpKeep contract , and repeated the same open-close cycle five times.

 Every trade in that batch was on pairIndex 0 , whose pairs(uint16) readout maps from = BTC and to = USD, with feed (under Event #1): 0x7404e3d104ea7841c3d9e6fd20adfe99b4ad586bc08d8f3bd3afef894cf184de 

 That same feed hash appears in the exploit transaction's price-request events. 

 The position opened at a delivered price of exactly $5,000 and closed, within the same atomic transaction, at roughly $60,000 . 

 Bitcoin does not have a 12x intra-block.

 Strip away the contract names and it comes down to this: Someone got Ostium's price-reporting system to accept a fake Bitcoin price as real, and the protocol paid out millions of dollars based on that lie.

 In plain English, the system did what it was built to do: Trust an authorized-looking price submission and execute against it, without separately checking whether the price made sense.

 Exactly how the attacker obtained the ability to submit that price is still unconfirmed.

 What is not ambiguous is that Ostium had already classified the relevant keeper path as trusted: Its Immunefi bug bounty scope says registered keepers and their forwarders , including PriceUpKeep and PrivatePriceUpKeep, are “assumed to be trusted and operating correctly,” and that issues requiring a compromised or malicious keeper are out of scope.

 The attack therefore used a path Ostium had excluded from bounty coverage. 

 What's the point of a bug bounty that pays you to ignore the one lock the attacker actually picked? 

## Kyber to Tornado

 Eight transactions. Five minutes and twenty-nine seconds from the first test-loop transaction to the final drain transaction . 

 $23.75 million extracted by time the damage was done. 

 The attacker opened with a $100 dry run , deposit, an $897.80 payout, close, confirming the exploit path worked before committing to anything larger.

 Twenty-five seconds later came the transaction that did most of the damage : A single executeBatch call, five nested loops, $11.86 million pulled from the vault in one shot.

 Six more standalone transactions followed at decreasing size, collecting a payout roughly ten times that size, then closing out for almost exactly what went in. The vault kept pennies. The attacker kept the rest.

 None of it stayed in USDC. The full amount moved through KyberSwap into 12,084 ETH , at an average execution price of about $1,966, then fanned out across 30 attacker-controlled wallets , a spread wide enough that no single address ever held enough to make an easy target. 

 PeckShield caught the next move : 10,540 of the 12,084 ETH deposited into Tornado Cash before the day was out. The wallet that started this whole thing had been funded, fittingly, with 1 ETH from ChangeNOW and 1 ETH from Bybit, a two-dollar-figure seed for a nine-figure heist.

 Arkham's own counterparty data tells a messier story than the clean $23.75M headline number.

 Ostium counterparty volume reads $29.04M . Kyber Network reads $47.07M , almost exactly double the real swap, the kind of number you get when both legs of a trade get counted as separate volume instead of one net flow.

 Tornado Cash sits at $22.47 million , as the attacker exited with most of the funds.

 Whatever the exact accounting quirks, the direction of travel isn't in dispute : As of this writing, roughly $4 million remains sitting across the attacker's 30 wallets.

 Everything else already went through the mixer. 

 Exploiter Address: 
 0x321Df194646029e7A6193Ea05573d4B9c398bfD9 

 Test-loop Transaction: 0x4b7ff5de823dd7af29cf1a6602a84d7b6eee354edcbaf0427fd5e691d3d80951 

 Main Exploit Transaction: 0x359f8c05b86a4409d60cfba02084334313fd94b19f74a294fb7fc4ea7d4870e0 

 6 Standalone Drain Transactions: 0x56e4139a2f51e99933479becee21812dd2ec656128f6f3593a7fa225e2f24adc 0x397daa6c23c87670f949a970961b1014e966cc40301a99b55c3c1908dd61418e 0xd9f91cc3eaec695f45bffad3a068fa52e1625ed44bfcc47d6ac3938f78d9061d 0x3b04639ab9b40760b2138e7bfa7eccc9657f3a767a5c414dbb1b3632ed71f3bf 0x6c254483fa47a14622662e792bc3728ab3c408a33d3cbb5712434ba96f5ecdc2 0xfaf6d3d4d7f1a75bfc11fb4d36d0525791546267fda1cdd371703ce03ae8ba8c 

 Ostium OLP vault (drained): 
 0x20D419a8e12C45f88fDA7c5760bb6923Cee27F98 

 Ostium TradingStorage (Proxy): 
 0xcCd5891083A8acD2074690F65d3024E7D13d66E7 

 Ostium Verifier (current, confirmed via Registry's ostiumVerifier update event): 0xd456939e54F68Ef9B0BE62aBB2EC4A37397Cb814 

 Replaced the prior address via a Registry update transaction dated February 14, 2026 (151 days before the exploit): 
 0xcCF233920e8cc9415ecF503b992881d69b6c47Ad 

 Ostium PrivatePriceUpKeep (exploited contract): 0xB71ec9eBD8145daCaCF6724363143cb5667A3d36 

 Ostium PriceUpKeep (public, not used in this exploit): 0x52B2a78E12b09B66C6c8ce291D653D40bAb77f0c 

 Ostium Trading (opens and closes each position, requests the price): 0x6D0bA1f9996DBD8885827e1b2e8f6593e7702411 

 Ostium TradingCallbacks (settles the trade on the delivered price, pulls the payout from the Vault): 
 0x7720fC8c8680bF4a1Af99d44c6c265a74e9742a9 

 Arkham entity page (30 linked addresses): 

 Arkham Page Link Here 

 Every one of those addresses is public, labeled, and sitting in plain view. None of that visibility buys a single dollar back. 

 When 83% of your stolen $23.75 million is already unlaunderable-back-into-existence, what exactly is left to "trace"? 

## Flagged and Filed

 Ostium was audited six times across three different firms over more than two years . The last of those reports closed just eight months before the exploit. 

 Zellic reviewed the contracts before mainnet in February 2024 , finding 19 issues including two critical. 

 ThreeSigma spent ten person-weeks on it the following month and found 57 findings , including two highs and one critical.

 Pashov came through twice in 2025 , in January and again in April .

 Zellic returned for a second full engagement that September , running until November of 2025.

 Pashov closed out the run this January 2026 with a 3rd audit. 

 Six reports, three firms , two-plus years of continuous outside review. 

 Ostium's own current documentation summarizes those first two engagements rather differently.

 Its audit page describes Zellic's findings as "no critical vulnerabilities identified in either engagement," and ThreeSigma's as "no critical or high-severity vulnerabilities."

 Except the actual audit reports say otherwise.

 Zellic's February 2024 assessment lists two Critical findings by name , traders able to increase collateral without paying for it, and an order-ID reuse due to multiple price-upkeep deployments, and ThreeSigma's own report includes one critical finding and two high findings of its own. 

 Zellic's own report confirms its assessment predated Ostium's Arbitrum deployment ; ThreeSigma's audit, running through that same pre-launch window a month later, marked its own Critical and High findings "Addressed" rather than left open . 

 But the official summary Ostium published describes audits that , on paper, missed the very findings its own auditors documented.

 Every one of those audits scoped smart-contract logic , including onchain price handling, not the offchain keeper and forwarder infrastructure supplying those prices.

 Zellic said so explicitly in its very first report : "Infrastructure relating to the project" and "key custody" were listed as out of scope. That's a standard, defensible boundary.

 Auditors get a pass here, this was never their job, at least for these engagements. 

 What doesn't get a pass is what happened after Zellic's second engagement, in November 2025. Section 4.8 of that report isn't a missed vulnerability . 

 It's Zellic actively flagging a risk they weren't being paid to fully investigate , in writing, eight months before the exploit: "By design, forwarders can cancel any order or action... These concerns are not a complete enumeration of the potential issues that can arise from a compromised forwarder."

 That is close to a preview of what happened on July 15.

 Ostium's response was to patch the one concrete example Zellic illustrated , a forwarder abusing REMOVE_COLLATERAL, and move on.

 The general warning that a compromised forwarder was a real , unenumerated risk category never became a follow-up audit scope item, never made it into the bug bounty program, and never triggered a broader review of the keeper trust architecture. 

 Instead, that same bug bounty program went on to state that registered keepers and their forwarders were "assumed to be trusted and operating correctly," with any finding requiring a compromised keeper explicitly carved out. 

 The risk wasn't undiscovered. It was named, dated, and filed. The buck for the gap between "flagged" and "fixed" sits with Ostium, not with the people who told them where the wall ended.

 The vault absorbed the consequence directly. Trader margin, by Ostium’s own account, remained unmoved in frozen trading contracts throughout .

 Ostium's public response ran the standard playbook : Pause trading, advise revoking contract approvals, confirm funds frozen and preserved.

 A late evening update cited fourteen hours of continuous coordination with SEAL 911 , unnamed authorities, and multiple security researchers, thanking the community for its help without adding a number, a mechanism, or a timeline. 

 Ostium's public account of what happened came in pieces. 

 A follow-up from Kaledora the night after the exploit confirmed positions remain open and frozen, and also promised "a technical post-mortem and outline of the path forward towards protocol restoration... over the coming days," and included a pointed warning: "Please trust only official channels. We are not circulating recovery forms and will never ask for your keys, seed phrase, or funds."

 Three days later, on July 18, Ostium's official account went further , offering its first real characterization of the mechanism: The attacker "compromised off-chain infrastructure related to the system that feeds prices into the protocol," then submitted "illegitimate price reports that were manipulated to appear as valid", opening and instantly closing a series of large positions to extract an artificial profit from the vault.

 That confirms infrastructure compromise rather than a smart-contract bug , consistent with everything traced in this piece, but it still stops short of specifying whether that meant a stolen signer key, a hijacked forwarder, or something else. 

 The same update named three additional security partners (Mandiant, zeroShadow, Collisionless) alongside SEAL 911 and law enforcement, said trading contracts were frozen within 60 minutes of the first exploit transaction, and confirmed trader positions will be marked to the price at re-open once trading resumes, independent of interim price movements . 

 A subsequent update said Ostium was working toward a relaunch within the week , with 24 hours' notice before trading resumes, positions marked to the live price at reopen, and a liquidity provider recovery plan Ostium said it intends to contribute from its own balance sheet, alongside new and existing partners.

 A full technical postmortem and reimbursement plan for liquidity providers still hadn't arrived by the time this piece went out.

 The laundering hadn't stopped either : Arkham's transfer feed for the exploiter's cluster shows additional 10 ETH deposits into Tornado Cash within hours of publication, on top of the balance already reconciled elsewhere in this piece.

 The mechanism is now on the record. What accounting for it looks like is not. 

 If the warning was already in writing eight months out, what exactly is left to postmortem? 

 Bitcoin was never at $5,000 that afternoon , and Ostium's own contracts paid out $23.75 million on the fabricated gap anyway . 

 Every safeguard that might have caught this had already looked past it by the time it mattered. 

 The oracle trusted its signer, the bug bounty trusted the keeper , and Zellic had written down, eight months early, that a compromised forwarder was exactly the risk nobody had fully mapped .

 Ostium patched the one example Zellic illustrated , marked the finding resolved, and treated the broader warning as closed.

 Six audits, three firms, two years of paying people to find what was wrong , and the thing that actually broke was never specifically anyone's job to check, per Ostium's own bug bounty scope . 

 That's not a story about a missing audit. It's a story about a warning that got acknowledged, patched around, and shelved instead of escalated.

 Ostium might survive this the way better-funded protocols have absorbed worse and kept building, and $23.75 million against ~$60.4 billion in lifetime volume is a bad week, not an obituary.

 But surviving isn't the same as answering for it, and eight months is a long time to sit on a warning that turned out to be exactly right. 

 If your own auditor tells you where the compromised door is, and you only fix the example they pointed to instead of the door they described, whose fault is it when someone finally opens it? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

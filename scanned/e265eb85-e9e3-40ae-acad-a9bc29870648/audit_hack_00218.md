# [C] Rhea Finance exploit: $18.4 million gone from the largest protocol in NEAR's DeFi ecosystem before most of its users had finished their morning coffee

## Summary
Severity: Critical
Target: Rhea Finance
Loss: $18,400,000
Published: 4/16/2026
Source: https://rekt.news/rhea-finance-rekt
Type: rekt-postmortem

## Details
## Rhea Finance - Rekt

 Tuesday, April 21, 2026 Rhea Finance - Swap Route Exploitation - Input Validation Failure 

 read this article also in : 

 42 hours of preparation . 123 fake tokens. 5 worker wallets dispatched within 10 seconds of each other. 

 $18.4 million gone from the largest protocol in NEAR's DeFi ecosystem before most of its users had finished their morning coffee. 

 Rhea Finance - formed from the 2025 merger of Ref Finance and Burrow Finance , which at its peak held more than 95% of NEAR's DeFi TVL - fell to an attacker who needed none of the usual tools.

 They needed something simpler: A protocol that trusted pools it had never seen before.

 The root cause was a flaw in Rhea's margin trading engine - a validation function that accepted a fabricated swap route as legitimate, borrowed real assets against it, and never checked whether what came back from the swap matched what it had just approved.

 So the attacker made their own pools . Minted their own worthless tokens. Seeded their own liquidity. And Rhea's oracle read every fake signal as gospel, then handed over real USDC, USDT, ZEC, and NEAR against collateral that was worth nothing . 

 What made this different from a hundred similar attacks before it was the exit. 

 Rhea had spent months building out its Zcash integration, a cornerstone of its ZcashFi narrative, a $54,200 grant application filed just three weeks earlier .

 The attacker used that exact infrastructure to route ~$4 million into Zcash's shielded pool , where zk-SNARKs make chain analysis cryptographically impossible.

 The feature Rhea was proudest of became the door the attacker walked through on the way out.

 Tether froze $3.29M . Near Intents caught another ~$3.3M mid-cashout .

 But ~$4M in ZEC is gone by design - not by luck, not by speed, but because the privacy guarantees Rhea was marketing as a product worked exactly as intended for someone who wasn't supposed to use them. 

 When a protocol's best feature becomes its attacker's best tool, what exactly was being built? 

 Credit: QuillAudits , DefiLlama , yellow , ZCash Community , Paolo Ardoino , CertiK , Rhea Finance , Defi Nerd , CoinDesk , CoinTelegraph , marina 
 Early on April 16, CertiK Alert was the first to name it . 

 "We have seen an incident affecting Rhea Finance. The attacker created fake token contracts and added liquidity in fresh pools, likely misleading the oracle and validation layer. In total, at least ~$7.6M was extracted."

 One wallet address. One transaction link. An initial figure that would later prove to be less than half the real number.

 Attacker NEAR wallet: 
 31ac7a2705a0686ff427b1a52d3ffd1fcfaa4b1f3cb3e83a0f767494e724a540 

 Rhea's first statement came a few hours after the attacker had already finished. 

 "The RHEA team is aware of an incident affecting the protocol. As a precautionary measure, we have temporarily paused the contracts while we conduct a thorough investigation."

 Controlled. Brief. And notable for what it didn't say: No figure, no affected contracts named, no indication of scope.

 The team had already reached out to the attacker directly , an on-chain message sent to the command wallet before the public statement was even posted.

 On-chain contact tx: 
 6r5c2iZighKJRcjXLkBbhQJxZ5dmzKTZDnqT7cmd8gh6 

 Before Rhea had finished drafting that first tweet , Tether had already moved.

 Paolo Ardoino, Tether's CEO, confirmed the freeze publicly on X : $3.29 million USDT linked to the attacker's wallet, locked before it could be converted or moved. "Tether cares." 

 The freeze was possible only because the USDT hadn't yet been touched. 

 What the attacker had already converted to USDC , specifically to avoid this outcome, was already gone.

 That deliberate swap, USDT to USDC mid-operation, was noted by independent researchers in the ETH Security Telegram before any security firm had published it, and their estimate of the total stolen was already closer to $20 million , not $7.6M. They offered to help trace the NEAR-side flows.

 On April 17, Rhea issued its full update , a multi-part thread that named the root cause for the first time.

 "Based on a preliminary analysis , the attacker leveraged a vulnerability in Rhea's Margin Trading feature to execute a coordinated pool manipulation attack." 

 Rhea Lend : Affected, paused.

 Rhea DEX : Not affected, paused as a precaution.

 rNEAR : untouched, not paused.

 The team confirmed it was in communication with the involved party regarding the return of remaining funds , had engaged a "leading security team" for forensics, and had notified law enforcement. No reimbursement plan. No total figure acknowledged. No post-mortem published.

 Also on April 17, QuillAudits published a detailed forensic thread with the most granular breakdown published to date: ~$18.6 million stolen across 1,142 transactions, 123 fake tokens, 5 worker wallets, and 42 hours of preparation before a single dollar moved.

 Rhea's official figure would later land at $18.4 million . 

 When your protocol is the target and independent researchers have a more accurate damage figure before you've issued a statement, who's actually watching the store? 

## The Oracle That Validated Nothing

 Most oracle exploits manipulate a price feed. This one manipulated the accounting that checked it. 

 The bug didn't live in Pyth and it didn't live in the Ref Finance DEX. 

 The failure lived entirely inside Burrowland's margin open-position validation , in a parsing function that counted the wrong thing and then never checked whether the swap delivered what it had just approved.

 To understand why, you have to start with the environment the attacker built before touching Rhea Lend at all.

 Preparation began as early as April 13. 

 Multiple accounts within Rhea's own Multichain Account system - including rhea000453.multica.near, rhea000462.multica.near, and rhea000505.multica.near - became active, later receiving funds traceable to the subject wallet. 

 The subject wallet itself was created on April 15 via a dust NEAR transfer , funded through intents.near within five minutes, then began distributing capital to dozens of intermediary accounts in rapid automated succession . 

 Multiple fake fungible-token contracts were deployed on NEAR on the morning of April 16.

 All of the fake fungible-token contracts shared the same code hash : BBeoVgxZC5Ce1ef7nErevX98QonNsedBFfqzep5RV1Vu

 All four failed to expose standard NEP-141 metadata methods , confirming they were purpose-built for price manipulation, not legitimate token contracts.

 Fake Token Contracts: c122aad2a188ed3abec0517f99c4dd03591d19e6bfcf7f015424351fbdd71163 7d06ad005e03aa875875481fb6a2bd1acf9e722100ab8747e4e97801ba340640 9c0df321dd5d9fc1138a09f405f523333fffe74de2ee10932ff756e27ae930ee 80f357d92e67f0ea53f299bb16d3af363ba0ef66e0211091edc2181cd323a705 

 Around those tokens, the attacker built a consecutive cluster of 25 liquidity pools on Ref Finance , pools 8514 through 8538 , structured in deliberate layers: ZEC paired against first-stage fake tokens, fake-to-fake cross-pools, and fake-to-USDC pools. 

 The pool graph wasn't random. It was designed to create a multi-hop swap route that repeatedly passed through USDC as an intermediate output before swapping it away again on the very next hop. 

 That structure was the weapon.

 Here's why…

 When a worker account opened a margin position through Burrowland using a Ref V1-style swap message, Burrowland's get_token_out() function parsed the route to calculate the minimum position amount - min_token_p_amount - that the trade was required to deliver.

 Burrowland's slippage protection summed all min_amount_out values across swap actions to derive a final expected output, but did not account for swap actions where the output token of one step is reused as the input of the next

 The attacker's route bounced through USDC repeatedly as an intermediate step : zec.omft.near → fake → fake → USDC → fake → USDC → … → fake → USDC 

 Every intermediate USDC leg had its own min_amount_out value. 

 Every one of those values got added together.

 The function never isolated the true terminal output , it summed all of them, treating intermediate hops as if they were final deliveries.

 Rhea's own incident report confirms the mechanism. 

 The result was an astronomically inflated min_token_p_amount that bore no relationship to what the route would actually return. 

 Burrowland then fed that inflated figure into the Pyth-based safety check - is_min_amount_out_reasonable() - comparing it against the real oracle-priced endpoint assets. 

 Because the attacker had crafted the route to make the inflated minimum pass that check , the validation succeeded. Burrowland emitted margin_open_started and dispatched the swap to Ref. 

 Ref executed the route faithfully. The real USDC that came back to Burrowland at the end of the path : 7,925 smallest units.

 The minimum Burrowland had just validated : 32,595,520,035,000,000,000,000.

 A gap of more than 4.1 million times .

 The following transaction shows a representative worker opening the poisoned margin position , the on-chain record of Burrowland accepting the inflated route minimum and dispatching the swap to Ref. 

 Worker margin open tx: 
 4H5kQ4HNWX4cqdksbwarbwmVZYVwRub25eWT2k97r1AN 

 When Ref sent the actual output back, Burrowland's on_open_trade_return() simply credited whatever arrived. No check against the previously validated minimum. 

 No second health factor calculation. No leverage check . The code only rolls back a margin operation when a swap fails entirely , when amount_in_used returns zero. Receiving a vanishingly small fraction of what was validated doesn't count as failure.

 It counts as success. Rhea's incident report confirms the borrowed assets were far below what slippage protection was expected to guarantee. 

 Burrowland emitted margin_open_succeeded. Position opened. Real assets borrowed against a position worth nothing. 

 Each opened position was worth far less than its debt, triggering immediate forced liquidations. 

 That cascade depleted the protocol's reserve pool and compounded the losses beyond the initial borrow . After the positions were open, the attacker removed liquidity from the fake pools , recovering the real assets that had been used to seed them.

 Each of the five worker accounts ran the same choreographed sequence independently: Deploy pools , seed liquidity , receive collateral from the master account , deposit into Burrow , open the poisoned margin position, withdraw , remove liquidity from the fake pools , transfer USDC and ZEC back to the master.

 Worker accounts: 
 d4e8e706f5a59610d85924af858f0562031930d14eb7add9a433edea50cf0b03 d39fd6da5eda882fe5f6716212552356cde2613054c670ffd6b49b3b25aef473 839810a1aef8ed1adb03e795b2a9785d783d4e2f415ab80c8b6fb30483e160f2 9053223460198e5e1e54dc15c18295ff0e98dca41ecd6c3872da1ff634d99616 5a7695e3626aeae7c0d340b6e58f813c71455d1be490eeb44e90bd9682343040 

 The fake pools served a dual purpose. They provided the multi-hop route structure that inflated the validated minimum.

 And once the position was open and the borrowed assets were in hand, the workers removed liquidity from those same pools and withdrew the real assets - USDC, ZEC - that had been used to seed them.

 The master account consolidated everything and forwarded it to the collector.

 Master account: 
 72633832db9d039b97906320169a8411bc2fa0f78303a4ecb1d35de71af621c5 

 Collector account: 
 31ac7a2705a0686ff427b1a52d3ffd1fcfaa4b1f3cb3e83a0f767494e724a540 

 The entire failure was Burrowland counting intermediate route minimums as final position guarantees, then treating whatever came back from Ref as an acceptable settlement regardless of the difference. 

 The code validated one economic reality. The protocol settled another. And nothing in between ever asked whether those two numbers were supposed to match. 

 When a lending protocol's safety check passes with flying colors while the actual swap delivers 4 million times less than validated, was the check ever protecting anyone? 

## The Ledger Doesn't Lie

 Once the positions were open and the borrowed assets were in hand, the operation shifted from exploitation to extraction. The blockchain kept every receipt. 

 Workers withdrew real USDC and ZEC from Ref Finance and forwarded them to the master account in parallelized batches. 

 Observed worker outputs ran around 109.54 ZEC and 7,661 USDC per worker , with additional ephemeral accounts forwarding chunks of approximately 10,583 USDC and 10,578 USDT .

 The uniformity of those batch sizes is more consistent with a scripted extraction pipeline than anything resembling normal trading activity.

 The master consolidated the proceeds and pushed them to the collector .

 Confirmed master-to-collector transfers as follows… 

 1,700,000 NEAR: 
 AJ42stVaKFsU2xYVZxzKFVRHvraeWgeEWxym7orJiGEY 

 460,455 USDC: 
 CXEnUrkeACi96BTNMJTbq4umK1EGFhnTfqJpieBMUd8F 

 446,582 USDT: 
 CHmaMXtnXrU9mBe3GYPPnGMMPT8ziKaJien9vdJ8VkPZ 

 799,903 wNEAR: 
 HuFrgaNEbvxZAgGBKD2k9VGfBaBhSYXjJhp632qAHhaW 

 7,095 ZEC: 
 6NyvczzGBdEDZtxsT7XYxcGD2fdSZcVrWdGX7sS1PE1p 

 From the collector, the full $18.4M basket moved through NEAR Intents in three deliberate steps. Internal transfer intents fanned funds across sibling wallets.

 ft_withdraw calls pulled real USDC back to NEAR. 

 And ft_withdraw on zec.omft.near routed ZEC directly into Zcash Unified Addresses , the fully shielded pool. 

 That last move wasn't improvised. The attacker had studied the exit routes before they ran the attack. 

 They knew Tether could freeze USDT. So mid-operation, before moving anything through Intents, they swapped USDT to USDC, a deliberate, premeditated counter to Tether's centralized freeze capability. 

 The USDT they didn't convert in time: Frozen .

 The USDC they had already swapped: Gone.

 $3.29M USDT frozen by Tether in the attacker's wallet, with an additional $1.05M USDT frozen within NEAR Intents - $4.34M in total frozen USDT . 

 ~$5.5M in USDC and NEAR recovered when Near Intents froze the attacker's account mid-cashout. 

 ~$4M in ZEC - 12,095 coins - routed into Zcash shielded pools, unrecoverable.

 The remaining $3.4M in USDC didn't stop on NEAR . It bridged to Ethereum, landed in the attacker's ETH wallet, and was deposited into Aave as aUSDC .

 Attacker ETH wallet: 
 0xbb5fa936469cadb8907f3aef80f5b53f55bc11f6 

 That position is traceable. Circle has the technical ability to blacklist USDC. Whether they act is a separate question. 

 Later the same day, the collector sent approximately 1,564,704 NEAR back to contract.main.burrow.near . 

 Collector-to-Burrow transfer: 
 Fe4JXLSq8iBJFTVRvo6ye48G8JGofuG5xfwUgfn55Yca 

 Rhea's official incident report confirms the attacker has since deposited approximately 3.359M USDC and 1.564M NEAR back into the RHEA lending contract.

 Additional assets have since been returned by the exploiter beyond those initial figures. The lending contract has been frozen to preserve those funds while recovery efforts continue.

 The full accounting as it stands: ~$5.5M returned or recovered via Intents freeze and mid-cashout intervention. ~$4.34M USDT frozen — $3.29M by Tether in the attacker's wallet, $1.05M within NEAR Intents. ~$3.4M USDC sitting as aUSDC on Aave Ethereum - traceable, not yet blacklisted. ~$4M in ZEC in Zcash shielded pools - gone. 

 Remainder still being traced across Intents solver outflows. 

 Rhea confirmed it is in communication with the attacker regarding the return of remaining funds and has notified law enforcement .

 Law enforcement notification is the easy part.

 The harder part is that ~$4M of this was designed from the start to end up somewhere no investigator can follow, routed through infrastructure Rhea had spent months building , actively marketing , and pitching to the Zcash community for grant funding just three weeks before the attack. 

 When the exit route was your own product, and the funds are already shielded, what exactly is law enforcement being asked to recover? 

## Similar Vulnerability, Different Chain

 This attack didn't arrive without precedent. The pattern has been repeating for years across every corner of DeFi, and nothing about it has become harder to execute. 

 Mango Markets, October 2022. Avraham Eisenberg inflated the price of MNGO through thin liquidity, borrowed against the inflated collateral, and drained ~$110 million . 

 He described it as a “successful and legal trading strategy.”

 A jury convicted him of fraud and market manipulation in April 2024 , though a federal judge later overturned those convictions.

 The mechanics were identical to what happened at Rhea - manufacture a price signal, borrow real assets against it, exit before anyone notices.

 The scale was larger. The outcome was the same. 

 KiloEx, April 2025: ~$7.5 million gone after an attacker exploited a custom price feed to set artificial entry and exit prices . Custom feed, no circuit breakers, no minimum liquidity requirements. 

 Makina Finance, January 2026 : ~$4.1 million drained through a permissionless AUM update function that pulled spot prices from manipulable Curve pools. Six audits, one expensive blindspot .

 The vulnerable integration was deployed after the last one closed. The exploit on Makina used the exact attack vector Cantina had listed as out of scope three months earlier. 

 YieldBlox, February 2026 : ~$10.97 million borrowed against USTRY collateral that had been pumped 100x in a single trade in a market with less than a dollar of hourly volume.

 The Reflector oracle reported what the market showed. Nobody had asked whether that market was worth trusting.

 Rhea Finance, April 2026 : ~$18.4 million. A margin validation function that summed intermediate route minimums as final guarantees. 

 Each attack is technically distinct. The underlying failure is not. 

 A Permissionless Surface: A DEX, a price feed, an oracle, a liquidity pool - gets treated as trusted input by a lending or margin system that has no mechanism to verify whether that input reflects reality.

 The attacker finds the gap between what the system validates and what it actually receives. Everything downstream runs exactly as designed.

 What separates Rhea from the rest of this list isn't the underlying failure. The gap between what the system trusted and what was real, that part was identical. 

 What separates Rhea is the operational sophistication of the person who found it. 

 Three full rehearsal cycles the day before. 123 fake token contracts. Five worker wallets dispatched within 10 seconds of each other. A deliberate mid-operation stablecoin swap to counter Tether's freeze capability .

 A shielded ZEC exit executed through infrastructure the protocol itself had built and was actively marketing to the Zcash community .

 This wasn't a trader who stumbled on a price discrepancy. It was a planned operation with contingency planning for the most likely intervention vectors.

 One community member's response to the CertiK alert on X is worth noting for context: "Panic is inappropriate. The hacker won't be able to withdraw coins from their wallet; this feature is disabled. That's the difference between near eco and other landings like drift or resolve." 

 That post landed before the ZEC exit had been confirmed. Before anyone knew that 12,095 ZEC had already cleared the shielded pool . Before the Ethereum Aave position had been identified . Before the USDT-to-USDC swap was understood for what it was. 

 Crypto theft reached $3.4 billion in 202 5, among the worst years on record, according to Chainalysis .

 Rhea adds to that total on a chain where 95% of DeFi TVL lived in one place . This wasn't a protocol getting rekt. It was an ecosystem.

 DeFi keeps shipping faster than its stress-tests. Auditors scope contracts. Nobody scopes the space between a permissionless DEX and the lending engine that trusts it. 

 When the same exploit pattern has now drained hundreds of millions across half a dozen protocols in four years, at what point does running it again stop being sophisticated and start being predictable? 

## What The Upgrade Didn't Cover

 Rhea wasn't operating without security infrastructure. That's what makes the questions harder. 

 In August 2025, Rhea announced Pyth Network as an official partner , providing real-time price feeds across its entire product suite. 

 The announcement was framed as institutional-grade infrastructure , the kind of oracle integration that separates a serious lending protocol from one that prices collateral off whatever thin pool happens to exist on its own DEX.

 Rhea's post-incident statements confirmed the vulnerability lived in the Margin Trading feature , and have not addressed why that feature wasn't using the same Pyth oracle infrastructure announced in August 2025 .

 A full post-mortem has not been published as of the time of writing.

 The ZEC timeline adds another layer. 

 Approximately three weeks before the exploit, Rhea submitted a $54,200 application to the Zcash community for the Rhea Zcash Gateway, a browser-based wallet and cross-chain DeFi integration for ZEC. 

 The application described enabling lending, borrowing, and liquidity access while preserving Zcash's privacy guarantees - allowing users to supply ZEC, borrow stablecoins, and access DeFi without losing privacy.

 The integration was new. It was being actively marketed through public roadmap posts and community grant applications. 

 And zec.omft.near - the withdrawal path the attacker used to route ~$4 million into Zcash's shielded pool - runs on NEAR Intents, the same cross-chain execution infrastructure Rhea had built its ZEC integration around . 

 The ZEC integration wasn't the vulnerability. It was the exit for ~$4M that no investigator can follow, formally approved three days before the attack . 

 Burrowland was audited twice by BlockSec before its March 2022 mainnet launch , with seven mid-to-low risk issues identified and fixed.[

 Margin trading was introduced as a V2 feature in July 2024 , more than two years after those audits closed. To the extent any review covered the margin path added in V2, it verified that the code did what it was written to do.

 The get_token_out() parser and on_open_trade_return() both executed as written. 

 Nobody asked whether a route could be designed to make that counting catastrophically wrong. 

 Nobody asked whether settling at the actual swap return, without rechecking the validated minimum, created a gap an attacker could drive $18.4 million through .

 Rhea had a partnership with Pyth . A 2026 roadmap full of cross-chain ambition and a freshly submitted grant application describing its ZEC infrastructure as a flagship product.

 None of it covered the margin parser. None of it enforced that what the route promised to deliver was what the protocol actually required to receive. 

 When you have institutional-grade oracle infrastructure and still get exploited through a pricing path it wasn't connected to, who exactly decided that connection wasn't necessary? 

 Rhea built the exit ramp and the attacker used it. 

 $18.4 million extracted from the protocol holding 95% of NEAR's DeFi TVL , taken through a margin parser that counted the wrong numbers and a lending engine that never checked whether what came back from the swap matched what it had just approved. 

 The attacker rehearsed it the day before. Studied the freeze mechanisms. Planned the USDT-to-USDC swap in advance.

 Routed the terminal exit through infrastructure Rhea was actively marketing as its flagship product .

 Tether moved faster than the post-mortem. Independent researchers had a closer damage figure before the team had finished its first statement.

 ~$4M in ZEC is gone permanently - not because recovery failed, but because the privacy technology worked. 

 Rhea has engaged security firms , notified law enforcement , and confirmed it is in contact with the involved party regarding the return of the remaining funds . 

 The attacker has returned approximately 3.359M USDC and 1.564M NEAR to the lending contract, with additional assets returned since. 

 Rhea has indicated it intends to use its protocol reserve fund and team operational resources as part of a compensation framework , the structure and scope of which are still being finalized.

 A detailed recovery plan , asset breakdown, and user support framework has been committed to and will be published once finalized. 

 Rhea DEX on NEAR is targeting a gradual reopening once all contracts have been reviewed and security hardened. 

 The questions that matter most - why the Margin Trading feature wasn't using Pyth , whether anyone reviewed the route parser for adversarial input, who stress-tested the ZEC withdrawal path before it went live - remain unanswered. No full post-mortem has been released.

 The code did what it was written to do. The protocol settled whatever came back. Nobody enforced that those two things had to match. 

 When a protocol can be drained by an attacker who understood its own architecture better than the team that built it, what does a security review actually certify? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

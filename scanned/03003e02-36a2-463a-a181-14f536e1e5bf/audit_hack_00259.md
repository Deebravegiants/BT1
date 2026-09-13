# [H] TAC exploit: Two days after MANTRA proved a halt could freeze what remained of an exploit in place , TAC proved that a halt can also be the moment you realize you

## Summary
Severity: High
Target: TAC
Loss: $7,500,000
Published: 8/22/2026
Source: https://rekt.news/tac-rekt
Type: rekt-postmortem

## Details
## TAC - Rekt

 Tuesday, September 1, 2026 TAC - Cosmos - Rekt 

 read this article also in : 

 Two days after MANTRA proved a halt could freeze what remained of an exploit in place , TAC proved that a halt can also be the moment you realize you were too slow. 

 On Aug. 22, an attacker exploited the same chain of Cosmos EVM vulnerabilities that had hit MANTRA two days earlier, draining 2,985,651,403.40 TAC from what Rarma identified as the network's bonded-token pool . 

 Cosmos Labs later confirmed the connection . The bulk of it was bridged to BNB Chain within 95 seconds .

 TAC halted at 23:58:11 UTC , roughly four hours and twelve minutes after the exploit began at 19:46:37 UTC .

 By then, the bulk of the funds was on another network , outside the control of TAC's validators. 

 SlowMist valued the drain at around $7.5 million .

 The same vulnerability chain. The same ecosystem. Two days apart. Two completely different endings.

 TAC says the flaw lives in code it does not own, that no new tokens were created , and that it is working with security researchers and exchanges to trace the funds that left the chain.

 As of September 1st, TAC still had not said how much, if any, of the funds it expected to recover. 

 If the same defense worked once, what has to be true for it to fail the second time? 

 Credit: MANTRA , Rarma , Slowmist , TAC , Daniele Berardinelli , Kiichain , Oraichain , Nesa , Arkham 
 TAC's first public statement came the same day as the drain, and it explained almost nothing. The team said it was investigating a vulnerability on the Cosmos-based EVM side of its chain, affecting only TAC supply, and working with validators on a temporary halt that will happen over the next few minutes. 

 No attacker named, no mechanism described, no figure attached.

 The chain was halted at block 24,671,475 .

 Then TAC went quiet for a day and a half.

 When Tac posted again early on Aug. 24, it filled in only what it chose to : A drain, not a mint; 2,985,651,403 TAC moved out of what the team called a single account; and a flaw it attributed to code it said it did not own. 

 A postmortem and a relaunch plan, it said, would follow the next day. 

 Neither arrived on schedule. TAC would offer a reason for that two days later , but not yet.

 What did arrive, hours later that same Aug. 24, was Rarma's independent forensic thread , filling in what TAC's public statement had not disclosed.

 Rarma named the specific contract call, identified the pool that emptied, and timed the bridge-out to 95 seconds , details absent from TAC's account.

 An outside researcher had supplied the transaction-level account , before TAC had explained what happened on its own chain. 

 When the chain's own team leaves the mechanism and movement of funds to outside researchers, whose account of the incident is doing the real explanatory work? 

## Not TAC-Specific

 TAC's total token supply never moved on Aug. 22. The vulnerability that drained roughly 28% of it lived one layer up, in code that TAC does not maintain . 

 The flaw traces back through the shared cosmos/evm codebase . 

 A pull request titled "Guard StateDB balance subtraction against underflow" was opened May 13 and merged into the module's main branch two days later.

 Independent researcher, Daniele Berardinelli, published a walkthrough of the underflow in late July, saying it had already been reported through HackerOne .

 The backport to the production release branches did not begin until Aug. 13, via PR #1253 and PR #1254 , and both backports were merged on Aug. 19.

 The v0.7.2 release notes described the update only as containing “important security fixes”. 

 The release notes carried no CVE , no public advisory, and nothing flagging the fix as a live exploit path. 

 KiiChain, hit by the same vulnerability family on Aug. 22, published one of the most detailed public technical accounts of the underlying bug .

 Cosmos Labs has since published its own detailed postmortem confirming TAC was attacked using the same chain of vulnerabilities as MANTRA , though TAC itself still has not published its own technical account.

 KiiChain describes an underflow in the staking precompile's write-back of a post-delegation balance to the EVM side , alongside at least two other defects it says remain undisclosed.

 TAC has confirmed none of that in its own words. 

 What it has said is narrower : The flaw sits in code it does not own, and the attacker drained what the team called a single account. 

 The transaction-level version comes entirely from Rarma .

 TAC has not published its own technical account, but Cosmos Labs later confirmed TAC was attacked using the same chain of vulnerabilities as MANTRA , identifying the exploit transaction and describing it as the same exploit chain.

 A MsgCreateVestingAccount call sent one utac to a contract the attacker controlled contract , used exactly once in TAC's entire chain history, seven seconds before the theft began.

 That vesting account then delegated one wei through the staking precompile , the same delegation path KiiChain's report describes as triggering the underflow there . 

 In the exploit mechanism Cosmos Labs later confirmed , the underflow was only the first half. 

 The attacker then sent the wrapped balance , roughly 2^256 tokens, to a victim account, such as a multisig or the 0x00 address.

 That triggered a second overflow : the victim's balance was reduced to zero while the attacker received the amount that had been there.

 The transaction was supply-neutral , but the attacker ended up holding real tokens taken from the victim account.

 Cosmos Labs' postmortem describes the two-stage mechanism. 

 Rarma flagged one difference worth sitting with. MANTRA's version of the exploit had the victim's address baked into the contract as an immutable value . TAC's took victim and beneficiary as calldata parameters instead, arguments supplied at call time rather than fixed in advance. 

 Whoever ran this a second time built something more reusable, not less.

 Supply itself never moved. Across the 4,976 blocks before the halt, there was no net supply increase; minting matched burning down to the individual wei .

 What broke was staking. Rarma found that validator records still showed 2,985,651,403 TAC as bonded .

 But the pool supposed to back that figure had a zero token balance , a complete on-chain shortfall. 

 If the bug lived in shared code from the start, and the pool it drained still hasn't been named by the team that ran it, what part of "not TAC-specific" is actually reassuring? 

## Scattered Stolen Funds

 The theft transaction and both bridge-out transfers are recorded on TAC's own explorer in sequence: The drain, followed by two separate cross-chain transfers, one moving roughly 500 million TAC and the other roughly 2.486 billion TAC , from TAC Chain to BNB Chain through LayerZero. 

 Combined, they account for nearly the full amount Rarma traced leaving the bonded pool in the first place . 

 Theft Transaction: 
 0xae4e9b708ecef134a18aef8a1da9b4d24aa2a0e87f98d02695beae588cda46fc 

 Bridge Transaction 1 (500M TAC): 0xa0581dbd3bd988ae28b7f397f83623d11b1870c05230e2dc04f27c9e581174c4 

 Bridge Transaction 2 (2.486B TAC): 0xce24d86fe536b5e04616795aa5cb923e5d3f7e2305be61c2ecdfd9c904b89e7c 

 Bridge Transaction 3 (49.9M TAC to TON): 0xe7ec92b8a6c19d94863e6c4bf3ad49428006e50549dd5387665f665be077b2d7 

 Attacker Address (TAC Chain): 
 0xecb0af97644d2c28c58369c663007a1b77c77c84 

 Same Attacker Address on BNB Chain: 
 0xecb0af97644d2c28c58369c663007a1b77c77c84 

 TAC's Aug. 24 statement says only that it is "working with SEAL 911 and with exchanges on the funds that moved." 

 Whatever additional movement TAC's coordination with SEAL 911 and exchanges has produced, it hasn't become public. 

 A follow-up on Aug. 26, explaining the team was holding its postmortem at Cosmos Labs' request , added nothing about a wallet freeze, a bounty offer, or a recovery figure.

 At the time of Rarma’s roughly 25-hour trace , there had been no swaps, mixer deposits, or exchange inflows. The same hexadecimal address that received the funds on TAC Chain was holding them on BNB Chain, in plain sight , where they landed.

 The same hexadecimal address that received the funds on TAC Chain was holding them on BNB Chain, in plain sight, where they landed.

 Cosmos Labs' Aug. 28 postmortem gives the fullest public account since : The attacker swapped approximately 1.2085 billion TAC for about 950,293 USDT across roughly 80 transactions on BNB Chain. 

 While additional flows included 115 million TAC bridged back to TAC Chain, where 65.1 million remains frozen in the attacker's wallet , and roughly 49.9 million TAC bridged to TON and sold . 

 Roughly 1.662 billion TAC remained unsold on the BNB Chain as of that publication.

 Cosmos Labs said the centralized-exchange accounts used by the attackers had been frozen pending investigation.

 TAC has not publicly said how much, if any, of the funds it expects to recover.

 That's the detail separating TAC's version of this story from MANTRA's. 

 MANTRA's incident stayed on one chain : No funds crossed a bridge, but 94.7% reached an exchange-deposit address before validators halted the chain. 

 TAC's halt came after the bulk of the funds had already left for another network . Whatever compensation or recovery TAC is building toward now has to run through negotiation, cooperation, exchange intervention, or law-enforcement action, not a reversal of the chain's own state.

 TAC has not publicly said what recovery process, if any, it is pursuing beyond its stated coordination with SEAL 911 and exchanges . 

 If an attacker who moved close to three billion tokens across a bridge in 95 seconds had left more than a billion sitting unsold for over a day, was that patience, leverage, or simply nowhere safer to put it yet? 

## No TAC Postmortem Yet

 TAC was not the last chain hit that week, and it was not the first either. 

 Rarma's post places TAC inside a wider cluster . 

 Oraichain, halted Aug. 9 after what its own team described as unauthorized ORAI minting through an EVM cross-chain transfer path , a different failure mode from the vesting-account drains that followed.

 MANTRA halted Aug. 20 . TAC and KiiChain both fell on Aug. 22.

 Nesa followed on Aug. 24, reporting an incident tied to the same underlying Cosmos EVM stack.

 KiiChain lost 148,326,583.15 KII across 18 repeated withdrawals on the same day TAC was hit. 

 Unlike TAC, most of it never left the chain : 54.4% remained frozen in attacker-controlled addresses, where KiiChain said it would move the funds to recovery wallets once the chain restarted . 

 KiiChain published a formal incident report within days of the exploit that named the mechanism outright and called the losses avoidable.

 Cosmos Labs’ Aug. 28 postmortem confirmed that MANTRA, TAC, and KiiChain were hit by the same chain of vulnerabilities : An unsigned-integer underflow in the Cosmos EVM balance-accounting layer, triggered by a crafted vesting account and a call through the staking precompile.

 Set against MANTRA and KiiChain, TAC's own disclosure looks thinner by the day.

 Both peer chains have published named mechanisms and their own accounting of what happened. 

 TAC has published three short statements and a follow-up explaining why its promised postmortem was delayed. 

 The delay has an upstream explanation, at least. Cosmos Labs first acknowledged an "ongoing security incident" publicly on Aug. 24 , four days after MANTRA's halt and two days after TAC and KiiChain were both compromised.

 It told chains running versions below v0.6.2 or v0.7.2 to halt immediately on Aug. 25 , six days after the patched release had already shipped without a public advisory at the time.

 A third statement on Aug. 26 said many affected chains had been patched , without naming which ones or putting a figure on what any of them had lost.

 Cosmos Labs published its Post-Mortem on Aug. 28 . TAC still has not published the postmortem it said would follow. 

 If two other chains running the same underflow-based vulnerability have already told their users what happened, in detail, what is TAC's postmortem still waiting on that theirs wasn't? 

 A halt only stops the bleeding it catches in time. 

 The central failure in this story traces back to a shared codebase. 

 A fix for an integer underflow was merged for three months before it reached a release branch, then shipped without a public warning that the vulnerability might already be live .

 MANTRA halted within 14 minutes of the drain that triggered it.

 KiiChain froze more than half of the stolen KII before its chain went dark.

 TAC's halt came roughly four hours after its funds had already crossed a bridge no validator vote could reach, a drain valued at around $7.5 million . 

 Two of TAC's peers have since told their communities exactly what happened, in detail TAC hasn't matched. 

 TAC has told its community that the bug isn't TAC-specific, that supply is intact , and that its postmortem is being held at Cosmos Labs' request .

 The pool an outside researcher identified as the source of the drain still has not been explained by TAC itself.

 Cosmos Labs has since accounted for the broad movement of the funds , including the roughly 1.66 billion TAC that remained unsold on BNB Chain , but TAC has not publicly provided its own recovery figure. 

 If a halt worked exactly as designed and some of the money still got away, what was it actually built to stop? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

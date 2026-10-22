# [C] Aave exploit: $27.78 million ( 10,938 wstETH ) in healthy positions liquidated - not by a hacker, not by a market crash, by Aave's own anti-manipulation system, mis

## Summary
Severity: Critical
Target: Aave
Loss: $27,780,000
Published: 3/10/2026
Source: https://rekt.news/aave-rekt
Type: rekt-postmortem

## Details
## Aave - Rekt

 Friday, March 13, 2026 Aave - Liquidation - Configuration Error 

 read this article also in : 

 The shield became the weapon. 

 $27.78 million ( 10,938 wstETH ) in healthy positions liquidated - not by a hacker, not by a market crash, by Aave's own anti-manipulation system, misfiring on the people it was built to protect. 

 Chaos Labs' Edge Risk engine pushed a single parameter update on March 10th.[

 Parameter Update: 

 0xfbafeaa8c58dd6d79f88cdf5604bd25760964bc8fc0e834fe381bb1d96d3db95

 AgentHub executed it one block later.

 Execution Transaction: 

 0x32c64151469cf2202cbc9581139c6de7b34dae2012eba9daf49311265dfe5a1e 

 The CAPO oracle, designed specifically to prevent artificial price manipulation, quietly capped wstETH at 2.85% below market rate , and Aave's liquidation engine did the rest.

 34 accounts,10,938 wstETH , worth $27.78 million. Gone before most users could refresh their dashboards.

 Note: wstETH is not ETH . It's Lido's wrapped staked ETH, a yield-bearing token that trades at a premium to ETH, accruing staking rewards over time. The gap matters when you're counting the damage. 

 No exploit code. No compromised keys. No bridge vulnerability. The most sophisticated oracle protection system in DeFi just disagreed with reality, and reality lost.

 Aave's Risk Oracle had streamed over 1,200 payloads across 3,000+ parameters without a single incident. Then this one broke $27.78 million worth of positions in a single block. 

 When your best defense becomes your biggest liability, what exactly were you defending against? 

 Credit: YAM , Aave , CoinGecko , Omer Goldberg , LTV Protocol , Stani Kulechov , Llama Risk , TokenLogic , CoinDesk , ACI , BGD Labs , Aave Labs , Carnation , QuillAudits , Moonwell , Chaos Labs 
 LTV Protocol was the first to surface the anomaly , posting on Twitter before Aave's official post-mortem landed. 

 Their observation was simple and damning : Aave's oracle was pricing wstETH at roughly 1.19 ETH.

 Meanwhile, the market ratio was approximately 1.228849 .

 That gap doesn't sound like much. For 34 leveraged E-Mode positions, it was everything.

 At 11:46 UTC on March 10, Chaos Labs' off-chain Edge Risk engine computed and submitted a snapshotRatio update to the wstETH CAPO oracle.

 AgentHub, the automated execution layer built by BGD Labs, picked it up and fired it on-chain one block later via Chainlink Automation . 

 No manual review. No human in the loop. One block from input to execution. 

 The liquidations followed immediately.

 On-chain monitoring accounts lit up.

 Early speculation on X ran hot.

 The words "hack" and "exploit" circulated before anyone had the full picture. 

 Chaos Labs moved fast. The wstETH borrow cap on both Aave Core and Aave Prime was reduced to 1. 

 Borrow Cap Reduction: 0x34f568b28dbcaf6a8272038ea441cbc864c8608fe044c590f9f03d0dac9cf7f8 

 The official post-mortem landed a few hours after LTV Protocol's post that spotted the anomaly .

 The diagnosis : Not a hack. A configuration mismatch between two parameters that were supposed to move together, and didn't.

 Omer Goldberg, Founder of Chaos Labs, was direct on Twitter : "Today, a misconfiguration on Aave's CAPO oracle caused wstETH E-Mode liquidations, resulting in a loss of 345 ETH. No bad debt was incurred, and all affected users will be fully reimbursed."

 Stani Kulechov followed with the corporate line : "A technical misconfiguration resulted in the liquidation of positions that were already close to their liquidation thresholds. There was no impact to the Aave Protocol." 

 A Lido contributor clarified to CoinDesk : “We are aware of the liquidations due to an incorrect wstETH to USD price reported by this oracle mechanism. The cause has nothing to do with wstETH itself, how it works or the Lido protocol which continue to operate normally.”

 Two responses. Two very different frames. Chaos Labs owned the technical failure and committed to compensation. Kulechov's statement quietly noted the affected positions were "already close to their liquidation thresholds", a framing that shifted some weight onto the users.

 Community reaction was not uniformly sympathetic to that framing.

 One detail buried in the independent reporting stood out : This almost happened a month earlier. A similar parameter mismatch had apparently been computed and submitted, but the CAPO wstETH agent wasn't yet connected to execute.

 The vulnerability sat dormant, loaded, waiting. This time, it executed. 

 When an outside observer spots the anomaly before the protocol does, and the same misconfiguration almost fired a month earlier without a single internal flag, at what point does "we moved fast to fix it" stop being the whole answer? 

## The Guardian That Broke

 CAPO wasn't a third-party price feed. It was Aave's own armor. 

 The Correlated Asset Price Oracle sits as a protective layer on top of the underlying Chainlink price feed - which, worth noting, worked perfectly throughout this entire incident. 

 CAPO's job was narrower and more specific: Cap how fast the wstETH/stETH exchange rate could grow, so nobody could artificially inflate collateral value and drain the protocol.

 The mechanism relies on three parameters working in lockstep : 

 A snapshotRatio - the anchor exchange rate. 

 A snapshotTimestamp - the time that anchor was set. 

 A maxYearlyRatioGrowthPercent - how fast the rate is allowed to climb from there. 

 Feed those three numbers the right values and CAPO computes a reliable ceiling. Feed it mismatched values and it computes a lie.

 Here's where a two-year-old stale anchor, and the rate limiter that kept it stuck, became a detonator.

 The wstETH CAPO contracts were initialized in early 2024 with a snapshotRatio of ~1.15 .

 On March 10, The Chaos Oracle did what it was designed to do . It computed the correct snapshotRatio update, approximately 1.2282, matching the exchange rate from seven days prior. 

 It also set the snapshotTimestamp to the intended seven-day-old reference point , exactly as the offchain algorithm designed. 

 Correct inputs. Correct logic. Correct answer.

 The smart contract said no.

 A built-in rate limiter , designed to prevent a compromised operator from spiking the ratio maliciously, capped any single update at 3% every 3 days .

 The existing on-chain ratio was ~1.1572 . Getting to ~1.2282 in one step would have blown past that ceiling. The contract could only accept an increase to ~1.1919 .

 The oracle didn't flinch , queried the contract, found the ceiling and submitted ~1.1919. 

 Exactly the fallback behavior the system was built for. Under normal conditions, where the previous snapshot is close to the current market rate, this is exactly what you want. 

 But the timestamp didn't face the same constraint. It was set to a seven-day-old reference point , exactly as the offchain algorithm designed.

 That created the mismatch that broke everything.

 CAPO now had a ratio anchored at ~1.1919 paired with a timestamp anchored seven days in the past, t elling CAPO to calculate forward from a reference point the ratio never actually reached.

 The formula extrapolated forward from a number that was too low. The computed ceiling came out at ~1.1939, below the live market rate of ~1.2285. Below, in fact, the rate Aave was already using. 

 Aave began pricing wstETH 2.85% below its actual value. 

 This misconfiguration resulted in the liquidation of positions that were already close to their liquidation thresholds .

 E-Mode made it worse. Efficiency Mode allows users to borrow at higher loan-to-value ratios against correlated assets , in this case, wstETH as collateral against WETH.[

 The higher the leverage, the smaller the price move needed to trigger liquidation. A 2.85% deviation that would be noise in a standard position was enough to push leveraged E-Mode positions across the line.

 Under normal conditions that's the feature, not the risk. Under a 2.85% artificial price deviation, it meant positions that had almost no real-world risk were sitting right on the liquidation line. 

 Liquidators swept through 34 accounts and 10,938 wstETH in short order. 

 The full liquidation list is visible on the Chaos Labs liquidation dashboard , filter by wstETH as collateral and WETH as debt, starting March 10.

 One detail makes this harder to dismiss as a freak accident. According to independent reporting from YAM , something similar had nearly triggered roughly a month earlier.

 The CAPO wstETH agent wasn't yet connected at that point , so there was no incident at the time.

 No alarm was raised. No review was triggered.

 The issue wasn't flagged, fixed, or even apparently noticed, and a month later, with the agent live, the system ran it again. 

 When your safety mechanism turns on your users and the near-miss a month prior went unnoticed, what exactly is the monitoring layer monitoring? 

## The Damage and The Windfall.

 The numbers were already established. 34 accounts. 10,938 wstETH . $27.78 million, not from a market in freefall, but from a protocol mispricing its own collateral. 

 No market crash caused it. No attacker triggered it. A 2.85% artificial price deviation, generated entirely within Aave's own protective layer, was enough to push every one of those positions across the liquidation threshold. 

 They were healthy in the real world and underwater on-chain, simultaneously, for the same moment that mattered.

 The liquidators were faster than anyone watching.

 The moment CAPO pushed wstETH's effective price below market, automated liquidators had an opening. They didn't need to know why the price was wrong. They just needed to know the protocol would let them act on it.

 Liquidators captured approximately 512 ETH in total. That number breaks into three distinct buckets, and the split matters. 

 Roughly 116 ETH came from standard liquidation bonuses , split between third-party liquidators and the Aave Liquidation Protocol. The system working as designed, just triggered by a false signal. 

 Another ~13 ETH came from liquidation fees. 

 The remaining ~382 ETH came from something harder to stomach: Pure arbitrage.

 Liquidators were buying wstETH from Aave at the protocol's artificially depressed price of ~1.1939 while the open market was still pricing it at ~1.2285

 That spread was free money for anyone positioned to act. They bought underpriced collateral from a protocol that didn't know it was underpricing, and sold it into a market that did.

 No exploit. No manipulation. Just arithmetic and speed. 

 When the only thing separating a user's collateral from a liquidation bot was two parameters falling out of sync, what exactly did the safety layer protect? 

## Clawing It Back

 Aave didn't accept the loss as final. 

 141.60 ETH was recovered from Titan Builder . 

 An additional 13.32 ETH came back through recovered liquidation fees. 

 Combined : Roughly 154.92 ETH returned before the DAO treasury was touched.

 That left a shortfall.

 On March 11, TokenLogic filed a Direct-to-AIP reimbursement proposal with exact figures : Total refund of 512.19 ETH, net cost to the DAO of 357.56 ETH after recoveries, with further recoveries still being pursued from builders involved in the incident.

 The proposal said the quiet part out loud : “The affected users bear no responsibility for these liquidations, which were the direct result of a protocol-level configuration error. Making these users whole is a straightforward decision for the DAO and reinforces the trust that underpins Aave’s position as the leading lending protocol.” 

 The governance response didn't stop at compensation. 

 Within hours of the AIP being filed , delegate ApuMallku posted a formal challenge : Support reimbursing users immediately, but demand the responsible service provider reimburse the treasury in turn.

 The framing was direct, if the DAO automatically absorbs the cost every time a highly-paid service provider makes a configuration error, it creates a moral hazard : "Skin in the game cannot just be a buzzword used during budget approvals; it must be enforced when operational oversights cost the protocol money. Let’s pay the users, but let’s also hold our vendors accountable." the post read.

 The question of who foots the bill beyond the users is now live in governance . 

 wstETH trading volume in the 24 hours surrounding the incident was only $10 million , low enough that no significant external party appears to have capitalized on the pricing mismatch in the open market before it was corrected. The damage stayed largely contained within Aave's own liquidation engine.

 No bad debt. No protocol insolvency.

 Just 34 users who did nothing wrong, liquidated by a system that was supposed to protect them, awaiting a governance vote on compensation for losses that should never have happened. 

 When the protocol calls it contained and the users call it a nightmare, whose definition of damage are we using? 

## Cracks Before the Collapse

 This didn't happen in a vacuum. 

 Seven days before the liquidations, Marc Zeller posted the exit letter that ended the Aave Chan Initiative's three-year run inside the Aave DAO. 

 ACI had been responsible for 61% of all governance actions, revenue strategies driving 48% of protocol income, and GHO's growth from $35M to $527M.

 Zeller's parting words were precise and unsparing . ACI had spent three years building a culture of accountability inside the Aave DAO. Transparent reporting, on-chain verification, delegate coordination, service provider standards.

 When they applied those standards to BGD Labs , the team requesting the largest budget in DAO history, [the system stopped working.

 The Temp Check vote that followed was decided by Aave Labs-linked addresses voting on their own budget , and it passed, 622,300 to 497,100, a margin Zeller's own post-vote analysis showed would have flipped without those addresses.

 In Zeller's words : "There is no role for an independent service provider in an environment where the largest budget recipient holds undisclosed voting power and uses it on its own proposals." 

 The other party in the dispute had also decided to leave. 

 BGD Labs announced they were leaving on February 20.

 The team that built and maintained the V3 codebase , the same codebase generating over $100M per year, posted that they would not be seeking renewal when their engagement concluded on April 1 .

 Their stated reasons went beyond any single proposal : Aave Labs' control of brand, communication channels, and voting power had created an organizational asymmetry they could no longer work around.

 In their own words : "We stop contributing because the environment no longer aligns with how we operate and where we see our value." 

 Two of Aave's most critical institutional pillars walked out the door within days of each other. 

 Shortly after, a misconfiguration in the automated risk oracle pipeline liquidated $27.78 million in healthy positions.

 Community reaction on Twitter was immediate. The connection was made within hours.

 Carnation dropped a tweet that said what could be on many people's minds : "Bad oracle update on Aave as soon as BGD Labs and Zeller decide to leave. Coincidence?" 

 No evidence connects the departures to the incident. The pipeline that failed was automated, the misconfiguration was technical, and Chaos Labs, still present and operational, responded and published a post-mortem the same day . 

 But the optics of a major operational failure in the immediate wake of two institutional exits are not something a post-mortem can fully neutralize. The question lingered.

 The politics made for better headlines. The technical record made for harder questions.

 The stale anchor, the rate limiter, the disconnected timestamp, those aren't contested. 

 So why did it take a live liquidation event to surface them? 

## The Pattern Nobody Wants to Name

 Aave wasn't an isolated case. It was the third act in a sequence that DeFi has been watching build for months. 

 In February 2026, Moonwell briefly priced Coinbase Wrapped ETH at approximately $1.12 instead of ~$2,200 , a configuration-level oracle error that left the protocol with nearly $1.78 million in bad debt . Not a hack. Not a manipulated feed. A misconfigured safety layer. 

 In the same month, attackers drained $10 million from YieldBlox's community-managed pool on Blend by manipulating a VWAP oracle reading from a market with less than $1 in hourly volume.

 The Reflector oracle reported accurately . The adapter passed the price through without a sanity check. The protocol accepted the collateral valuation without question. Every component performed exactly as designed, and the pool bled out anyway .

 Aave completed the sequence, not with an attacker, not with a manipulated feed, but with a protective mechanism that had been left to drift since February 2024, when the CAPO wstETH contracts were first initialized with a snapshotRatio of ~1.15 , and never reconciled with the market it was supposed to be tracking.

 A rate limiter that prevented correction as effectively as it prevented manipulation. A timestamp that advanced while its paired ratio couldn't follow. The anti-manipulation cap set below reality. 

 Three incidents. Three different protocols. Three different technical failure modes. One shared architecture of failure: The gap between what the safety layer was designed to handle and what the real world actually delivered. 

 Moonwell's oracle mispriced a wrapped asset by orders of magnitude. YieldBlox's oracle faithfully reported a price from a market that had effectively ceased to exist. Aave's oracle cap fell below the live rate because a stale 2024 parameter couldn't catch up to two years of normal yield growth.

 None of these were exotic attack vectors. All of them were configuration problems hiding in plain sight.

 Audits verify that contracts behave as written. They don't verify that what's written still reflects reality six months, or two years, later. The threat model keeps evolving. The review cadence isn't keeping pace. 

 When three protocols in a couple of months are undone not by hackers but by their own safety infrastructure, is this still a series of isolated incidents, or is it a design philosophy reaching its limits? 

 Aave's anti-manipulation system worked exactly as written , and that was the problem. 

 Two parameters drifted out of sync, an automated pipeline executed without pause, and 34 users paid for a misconfiguration that had been quietly building since 2024. 

 The code was correct. The configuration was not.

 That distinction will matter less to the people who got liquidated than it does to the people writing the post-mortem.

 What makes this harder to dismiss than a simple ops error is the apparent near-miss a month prior , the same mismatch, computed and submitted, stopped only because the agent wasn't yet connected.

 Nobody caught it. Nobody flagged it. The vulnerability reloaded and waited.

 A note on classification: No external attacker drained these funds. What happened was a protocol-level configuration failure that triggered legitimate liquidations of healthy positions. By Rekt News standards, users lost money because a system broke. 

 DeFi keeps building faster than it audits, faster than it monitors, and apparently faster than it notices when its own safety systems are primed to misfire. Aave will compensate the users. 

 Chaos Labs will review the parameters. The DAO will debate governance.

 One footnote worth reading slowly. Chaos Labs' own renewal proposal to the Aave DAO describes the Edge Risk Oracle as their "top priority", a system that "currently secures over $5B in deposits."

 Their website describes their oracle infrastructure as providing "real-time anomaly detection and circuit breakers to protect protocols from oracle exploits."

 The Aave DAO treasury has been proposed to cover losses caused by that same oracle.

 And somewhere on another chain, another stale anchor could sit unchecked. 

 When the system that protects you becomes the system that liquidates you, and the only thing that stopped it last time was a disconnected wire, how many connected wires are you still not looking at? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

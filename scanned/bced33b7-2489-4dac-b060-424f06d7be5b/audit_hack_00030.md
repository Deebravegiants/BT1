# [H] Aztec Connect exploit: $2.28 million drained from a contract nobody was watching - two separate attackers, the same flaw, on two consecutive mornings, three years after Azte

## Summary
Severity: High
Target: Aztec Connect
Loss: $2,280,000
Published: 6/14/2026
Source: https://rekt.news/aztec-connect-rekt
Type: rekt-postmortem

## Details
## Aztec Connect - Rekt

 Thursday, June 18, 2026 Aztec Connect - Aztec Labs - Rekt 

 read this article also in : 

 $2.28 million drained from a contract nobody was watching - two separate attackers, the same flaw, on two consecutive mornings, three years after Aztec Labs walked away. 

 Aztec Labs had deprecated Aztec Connect in March 2023 , and handed back the admin keys in April 2024 , and left the contracts exactly as they were - immutable, unmonitored, and still holding every dollar its remaining users had never claimed. 

 The $2.28M sitting inside it was not a secret. Neither was the source code.

 The attacker found a gap between two systems that were supposed to be talking to each other but weren't bound together, a ZK proof that verified one transaction set, and a settlement layer that executed against a different one .

 What went in one end did not constrain what came out the other.

 Fourteen rollup proofs across seven assets, extracted in a single atomic transaction - not by breaking any cryptography, not by compromising any key, but by exploiting a logic flaw in a contract that could no longer be paused, upgraded, or answered for. 

 The following morning, a second attacker returned to the same vulnerability , submitting 14 more rollup calls across a fresh wallet and sweeping the residual DeFi bridge positions the first drain had left behind, another ~$88K gone before the day was out. 

 Three days later, a third attacker hit a different Aztec contract through a different entry point entirely, and was drained for another ~$2.2 million .

 A separate story. The same pattern. The same broken architecture.

 Behind it sat about $100M in VC backing , ZK research dating back to Aztec's 2017 founding , and a $450,000 bug bounty paid out for a critical flaw caught on the same codebase in 2023.

 Admin keys made that fix possible.

 By the time this flaw surfaced, those keys had been gone for over two years . 

 When a protocol's last line of defense is the hope that nobody reads its open-source code, how long was that defense ever going to hold? 

 Credit: Aztec Labs , TechCrunch , Aztec Network , Aztec Foundation , CertiK , BlockSec Phalcon , Odysseus , Syscoin , Blockaid , SlowMist , Defimon Alerts 
 Before the names blur, four separate entities appear in this story and they are not interchangeable. 

 Aztec Labs is the company that built and operated Aztec Connect , then renounced control of its contracts in April 2024 .

 Aztec Connect is the legacy zk-rollup privacy infrastructure that was deprecated in 2023 , its contracts now immutable and holding the exploited funds.

 The Aztec Foundation is a separate legal entity that posted a public statement on the day of the exploit but holds no operational role over the deprecated contracts.

 The Aztec Network is the current live product Aztec Labs pivoted to after deprecation , built on the Noir ZK language and unaffected by this incident.

 The exploit executed at 12:26 UTC on June 14th . Aztec Labs identified it internally four minutes later. 

 Then the clock ran. 

 CertiK was first to go public , 86 minutes after the drain - naming the attacker address, publishing the transaction hash, and putting a $2.19M figure on what had just happened to the Aztec Connect Router contract .

 CertiK's second post sharpened the mechanism : computeRootHashes() only validated the beginning of the submitted _proofData, while the parameters controlling actual token transfers sat in the middle, unchecked and functionally invisible to the proof.

 BlockSec Phalcon flagged the same transaction independently : Identifying the root cause as a mismatch between the verified rollup transaction set and the L1 settlement processing boundary, numRealTxs was not effectively bound to the transaction set enforced by the ZK proof, allowing the proof verification path and the settlement logic to interpret the transaction list differently.

 Odysseus, founder of phylax.systems, cut through both in a single thread : This hit the legacy Aztec Connect rollup, not the current Aztec Network stack. The transaction batched 14 valid processRollup calls into RollupProcessorV3, executing public withdrawals. The L1 trace showed withdrawals - not an admin sweep, not an ERC20 approval drain. 

 CertiK had been public for 74 minutes before Aztec Labs said anything. 

 When the statement finally came , it was four sentences and transaction : "We are investigating a potential exploit affecting Aztec Connect. ~$2.1m was transferred from the immutable smart contract in a transaction . Aztec Connect was deprecated 3 years ago. Aztec Labs holds no admin keys or control over the system; it cannot be paused or upgraded by us. We will share further updates in due course.”

 The Aztec Foundation followed two minutes later with one clarification that mattered : No connection between the deprecated contracts and the AZTEC ERC-20 token or the current Aztec Network.

 Two posts, neither containing a technical detail, a timeline of how the funds were taken, or any commitment to a postmortem. What they were sitting on would only come out later.

 Syscoin, hit by a bridge exploit one week earlier , had published a detailed preliminary post-mortem before most of its users were awake - they named the flaw, published all transaction hashes, identified the tainted wallets, confirmed a fix was in place.

 Aztec Labs had no fix to offer and no funds to recover. But they had information, and they sat on it. When a team no longer has admin keys, transparency is the only lever left, and for the first several hours, Aztec Labs didn't reach for it. 

 The full technical account, when it came, was thorough . But it came after everyone else had already filled the silence. 

 Blockaid had flagged a pre-exploit contract deployment from the attacker's wallet, approximately six minutes before $2.19M left the contract .

 Aztec Labs later credited the detection explicitly . But, six minutes wasn't enough.

 Defimon Alerts stepped in with the most granular breakdown of any early alert : 909 ETH, 270,513 DAI, 167.89 wstETH, plus LUSD, yvDAI, yvWETH, and yvLUSD. The attacker EOA was fresh, with only nine transactions to its name, and the wide mix of asset types was inconsistent with any single legitimate depositor exit.

 SlowMist published a full technical analysis the following day , an independent forensic reconstruction from open-source contract code and raw on-chain calldata. 

 They named the flaw something none of the earlier alerts had : Settlement boundary bypass. 

 In the midst of the initial reporting, a second attack emerged.

 At 20:28 UTC on June 14th , eight hours after the first drain, a fresh wallet was funded via a relayer contract.

 By 04:00 UTC on June 15th , 14 more rollup submissions had begun, picking up exactly where the first attacker stopped, targeting the residual DeFi bridge positions the first drain had left behind.

 Another ~$88K gone before the day was out . Same flaw, same contract, different wallet. The door had been left open and someone else walked through it. 

 One more detail sitting quietly in the background : on March 17, 2026, Aztec Labs' own team had discovered a critical vulnerability in the current live Aztec Network, unrelated to this exploit, with a fix planned for the v5 release in July. The actual bug and corresponding patch will not be publicly disclosed until v5 . 

 A deprecated contract losing $2.28M across two consecutive mornings, and a live network carrying an undisclosed critical bug.

 A team that wrote the code, ran the sequencer, and chose the sunset terms, and when the contract was drained, had nothing left to offer but a statement. 

 What does accountability look like when the architecture makes intervention impossible? 

## The Boundary Break

 Every Aztec Connect rollup bundled a batch of individual transactions, what the protocol called rows . Two separate subsystems acted on each batch. Neither was bound to the other. 

 The first was the ZK validity proof. 

 Its job : Guarantee that balances added up, that nothing was created from nothing, that the new state followed correctly from the old.

 For efficiency, the proof processed rows in fixed-size groups of 32 . Even when only a handful of rows in a group were actually used, the proof was still checked and committed to the whole group.

 The second was the L1 settlement code, the Ethereum contract itself.

 It didn't re-examine every row. Instead it trusted a single number carried inside each batch called numRealTxs , which declared how many rows were real, and acted on only those. 

 The proof committed to a full inner-rollup chunk of 32 rows. The settlement loop stopped at numRealTxs. Same calldata, different boundary. 

 The L1 relied on the proof to make everything after numRealTxs harmless. The proof made no such guarantee.

 That misplaced trust was the exploit.

 The attacker set numRealTxs = 1 in each of the 14 calls to processRollup(), while packing two state-changing rows into the calldata.

 The proof committed to both , they fell inside the first 32-slot inner-rollup chunk. The L1 settlement loop processed only row 0. Row 1 was accepted by the proof and carried into the rollup state transition, but never reached the L1 deposit accounting layer. 

 Row 1 was where the deposit went . A large one, sized to match the exact withdrawal that would follow. 

 Because row 1 sat past the numRealTxs boundary, processDepositsAndWithdrawals() never ran for it . Consequently, decreasePendingDepositBalance() was never called . No funds were collected.

 But the proof had already committed to that deposit as real, the rollup state updated as if the money had arrived . The attacker held balance the contract believed was legitimate and wasn't.

 The withdrawal came next , placed at row 0 - inside the boundary, fully processed by the L1 settlement layer. Real assets transferred to the attacker's wallet.

 This was the full playbook across the 14 rollups : In the first seven, a harmless send transaction sat at row 0 while a fake deposit accumulated invisibly at row 1. In the final seven, the fake balance was cashed out, one real withdrawal at row 0, one asset at a time.

 Aztec Labs' own incident report put it plainly : "It is possible to submit a row that is accepted by the proof, but that the settlement code never processes. These checks would ensure, for example, that a deposit into an account was based on real funds sent to the rollup. So internal balances of users can be updated without legitimate deposits." 

 Aztec Connect deposits were two-stage by design . First, depositPendingFunds() pulls real ETH or ERC-20 into the RollupProcessor and increments a pending deposit balance. 

 Second, a counted deposit proof row consumes that pending balance - at this point, the L1 checks authorization and decrements the pending amount.

 The attacker's deposit rows were placed at row 1 , outside the settlement boundary. The second stage never ran. The pending balance was never decremented. No real funds ever backed the credited balance. The ZK proof had already stamped the state valid.

 The root cause was not a missing access control check , processRollup() being publicly callable after the sunset was a contributing condition, not the vulnerability.

 But the open door didn't empty the vault. The numRealTxs boundary mismatch did that . 

 SlowMist named it accurately : A settlement boundary bypass. 

 The cryptography never failed. The ZK proof did exactly what it was built to do. The flaw was in the contract that trusted the proof to enforce something the proof was never asked to enforce.

 If either subsystem had held the shared boundary rule , if L1 had rejected state-changing rows placed past numRealTxs, or if the circuit had treated those rows as neutral padding, none of this works. Neither did. Each assumed the other was covering the gap.

 Nobody was. 

 Was this a flaw that had always been there, quietly waiting, or one that arrived with the April 10, 2024 contract upgrade that reportedly shipped without an external audit ? 

## The Tally

 The first attack was clean, contained, and total. 

 At 12:26 UTC on June 14th, a single atomic transaction routed through the primary helper contract and made 14 calls into the Aztec Connect proxy contract . 

 Seven of those calls were withdrawals . Each one targeted a different asset - ETH, DAI, wstETH, yvDAI, yvWETH, LUSD, and yvLUSD - and cleared it from the contract.

 In under a minute, everything landed at the attacker’s EOA.

 Attacker EOA: 
 0x0F18D8b44a740272f0be4d08338d2b165b7EdD17 

 Attack Transaction: 0x074ec9317d8336db37e8c348fbdd7515573ff4088239c77ab429f522509aeeb1 

 Aztec Connect Proxy (Attacked Contract): 0xFF1F2B4ADb9dF6FC8eAFecDcbF96A2B351680455 

 RollupProcessorV3 Implementation: 
 0x7d657Ddcf7e2A5fD118dC8A6dDc3dC308AdC2728 

 The wallet had been funded via Tornado Cash at 09:26 UTC on June 14th , nearly three hours before the exploit was executed.

 Tornado Cash Funding Transaction: 

 0x3f05b03123008175b07b3f6ee4c5cefa402ed33873208790c1ee8fac5e46634e 

 Between 12:16 and 12:26 UTC, the attacker deployed five contracts in a ten-minute window . The preparation was deliberate. The timing was tight.

 Primary Attack Contract: 
 0x06f585F74e0DA633Ae813A0f23Fb9900B61d0fcD 

 Intermediate Helper Contract 1: 
 0xE810F602aa8B45Cc565f93E2141e740F0a640BCE 

 Intermediate Helper Contract 2: 
 0xd10916A49e09321C983f0dFD8a546aE83Fb0E0f8 

 Intermediate Helper Contract 3: 
 0x276E972ffD99bD8dF705dB3F735a95F655CcF6eC 

 The full take : 908.99 ETH, 270,513 DAI, 167.89 wstETH, 4,873.86 yvDAI, 16.57 yvWETH, 9,273.73 LUSD, and 359.05 yvLUSD. 

 Approximately $2.19 million at the time of the exploit. 

 No same-block offsetting flows. No round trip. The Aztec Connect proxy transferred to the attacker. The intermediate helper contract held nothing when it was done.

 As of June 15th, one full day later, SlowMist confirmed that 100% of the first attack's funds remained intact at the attacker's EOA . Nothing has moved and nothing has been laundered.

 Then, eight hours after the first drain, the door opened again .

 At 20:28 UTC on June 14th , a second fresh wallet was funded with 0.1 ETH via a relayer contract. 

 Not confirmed as the same attacker - different wallet, different setup, funded separately - but the same vulnerability, the same contract, and the same playbook, like they were a poacher looking for scraps. 

 Second Attacker EOA: 

 0x7ec9F769d932D3f716949E7ca3E079b7817d06DB 

 By 04:00 UTC on June 15th , the second attacker was submitting rollups, picking up at rollupId 13,291, exactly where the first had stopped at 13,290.

 Fourteen more calls, running through 05:17 UTC, targeting what the first drain had left behind : The residual DeFi bridge positions accumulated inside the rollup contract during Aztec Connect's active years.

 The second haul was more complicated to extract . The positions weren't direct deposits, they were wrapped yield-bearing tokens from Aave, Compound, and TroveBridge. 

 wa2WETH, wa2DAI, and wcDAI were moved out through the same boundary bypass , then redeemed from the attacker's wallet outside Aztec Connect, wa2WETH unwound to WETH and then ETH, wa2DAI and wcDAI unwound to DAI. 

 The TroveBridge position required one extra step : The attacker sent the TB-275 token back into the rollup contract, which converted it to ETH and sent it back out.

 The Euler-wrapped WETH, weWETH, was extracted but carried no redeemable underlying WETH at the time of the attack .

 Second attack assets: 36.39 wa2WETH, 6,706.26 TB-275, 3,220.84 wa2DAI, 622.74 wcDAI, 42.82 weWETH.

 Approximately $88K. 

 Aztec Labs published the intermediary wallet addresses in truncated form . The full addresses, verified on-chain, are as follows. 

 Intermediary Wallet 1: 

 0xC431a54943821339642f1073BBa884170Ba8C1f5 

 Intermediary Wallet 2: 

 0x0af71cd94A0305289ab2b337a1Da5D8e6CEf9912 

 Aztec Labs’ incident report identified the final destination as a high-volume service contract with roughly 1,900 depositors. Once tracing the actual address hash, it turned out to be Tornado Cash . 

 Combined across both attacks : Approximately $2.28M.

 The first attacker took the principal, unclaimed user deposits sitting in the contract since deprecation.

 The second swept the residue, three years of DeFi bridge positions nobody had unwound. Between them, they emptied everything the vulnerability made reachable.

 The first attacker's funds haven't moved. The second attacker's funds are gone. 

 Two attackers, two mornings, one open door, and the team that built it had been gone for over two years. Who exactly was responsible for what was left inside? 

## What Was Left Behind

 The Aztec Connect exploit did not impact the current Aztec Network. 

 The exploit had a minimum impact on the AZTEC token , up slightly on the day, the market reading the ring-fencing correctly. The current network’s users were never at risk. 

 But the users whose funds were sitting in the deprecated contract, the ones who hadn’t withdrawn in the year Aztec Labs urged them to , who couldn’t withdraw through the escape hatch once Aztec Labs stopped running the sequencer, who may not have even known their assets were still there, had no recourse . No compensation plan, and no recovery mechanism.

 Aztec Labs gave users over a year of notice , published reminders, built the exit infrastructure, and did what protocol teams are supposed to do during a sunset. And yet millions remained in the contract when the first attacker came for it.

 Aztec Connect sits in a category of its own among 2026’s growing list of exploits - not a live protocol, not an active bridge, not a team still running operations.

 A deprecated system, fully wound down, fully immutable, and now fully drained. 

 A zombie contract in the truest sense, dead to the team that built it, but very much alive to anyone who wanted to read the source code. 

 The industry keeps relearning the same lesson through different protocols. Deprecation is not deactivation. Immutability is not safety.

 An open-source contract holding real assets is a public invitation, with no expiry date, for anyone patient enough to find the gap.

 The attackers found it. Then someone else came along and picked up what they left behind. 

 When a protocol winds down but its contracts live on forever, who exactly is responsible for what happens next? 

 Aztec Connect wasn't hacked because the cryptography failed. 

 It was hacked because a proof system and a settlement layer were never required to agree on the same thing, and nobody was left who could make them. 

 The $2.28M is gone, but the more instructive number is zero - zero active audits, zero bug bounty coverage, zero monitoring, zero ability to respond.

 That's not a security posture. It's a contract running on borrowed time in a public environment, holding other people's money, with its source code available to anyone with a browser and patience.

 The users who lost funds followed the rules. They used a protocol that was audited, maintained, and backed by serious money.

 Then, three days later, a third contract and a different entry point. Aztec's deprecated infrastructure was still being read . 

 This time, the exploit came through the Escape Hatch circuit , allowing invalid proofs to pass on-chain - draining another ~$2.2 million . 

 The gap remained.

 A separate Rekt News story is coming soon covering the June 17 Private Rollup Bridge exploit: The Escape Hatch vulnerability, the attacker, and the drain.

 This wasn't Aztec Connect alone. It was the entire pattern of deprecated infrastructure left on-chain.

 The rug wasn't pulled. The product was sunset responsibly. And yet the outcome was the same. 

 If responsible deprecation still results in users losing millions to a flaw nobody caught, what does the industry actually owe the people left holding the bag when the sequencer goes dark? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

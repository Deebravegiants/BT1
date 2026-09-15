# [H] Mantra exploit: 720,923,967.99 MANTRA left two MANTRA-managed wallets on Aug

## Summary
Severity: High
Target: Mantra
Loss: $3,600,000
Published: 8/20/2026
Source: https://rekt.news/mantra-rekt
Type: rekt-postmortem

## Details
## Mantra - Rekt

 Monday, August 31, 2026 Mantra - Cosmos - Rekt 

 read this article also in : 

 720,923,967.99 MANTRA left two MANTRA-managed wallets on Aug. 20, worth roughly $3.6 million at the pre-incident spot price . 

 94.7% of it reached a single exchange deposit address before MANTRA ever halted the chain ; the halt froze only what remained. 

 MANTRA's own postmortem confirms the failure sat one layer down : A chain of two vulnerabilities in the balance-accounting layer of the shared Cosmos EVM module, the same open-source stack relied on by other chains whose teams may not have independently audited every component.

 An unsigned-integer underflow gave the vesting account an artificially inflated EVM-side balance.

 The attacker then used that wrapped balance in a transfer to a victim account , the burn address or the genesis multisig, producing an overflow that left the attacker holding what the victim lost.

 An attacker's contract, routed through the staking precompile , debited MANTRA's wallets directly, without the private keys, and the stack allowed it to happen. 

 This was MANTRA's second major crisis in sixteen months, following the insider-dumping collapse that erased roughly $5 billion in April 2025, as detailed in rekt's prior reporting, "Mantra of Misfortune" . 

 This time, the team moved quickly : It halted the chain 14 minutes after the second unauthorized transaction, then patched the network and resumed block production 30 hours and 13 minutes later.

 Three more chains would be compromised in the same week by attacks linked to the Cosmos EVM vulnerability cluster.

 MANTRA’s own postmortem, published Aug. 28, confirms the root cause : An unsigned-integer underflow in the balance-accounting layer of Cosmos EVM, triggered by a specially constructed vesting account and a call through the staking precompile.

 As of that publication, none of the extracted funds had been recovered. 

 The bug is confirmed. The halt worked as a containment mechanism, but only for what remained. Eight days later, why hasn’t a single token come back? 

 Credit: Rarma , MANTRA , Grey Ledger , Cosmos Labs , TechTimes , CoinDesk , TAC , KiiChain , Nesa , De , Protos , The Coin Republic 
 MANTRA broke the news itself. 

 On Aug. 20, the team posted only that it was "aware of an incident," had frozen the chain as a precaution, and had no root cause or timeline to share.

 No amount, no addresses, no name for what had gone wrong.

 Roughly nine and a half hours later, a second post narrowed things slightly : The incident was isolated to the Cosmos EVM module, two MANTRA-managed wallets were affected, and no user funds had been touched.

 Still nothing on how much. 

 The accounting came from somewhere else, at first. 

 Rarma traced the drain to two sources : 600,000,035.55 MANTRA from the null/burn address and 120,923,932.44 MANTRA from a genesis-era multisig.

 The funds moved through a single attacker wallet , which fired 24 transactions before going quiet.

 Rarma initially assigned the theft zero realized value because , at the time of his analysis, nothing had left the chain to be sold.

 MANTRA's own postmortem, published Aug. 28, put a different figure on it : Roughly $3.6 million, at the pre-incident spot price of $0.005 per token.

 It took MANTRA eight days to publicly confirm the amount and mechanism that Rarma had pieced together from public transactions within hours. 

 What was worth protecting in that gap? 

## One Day Too Late

 The confirmed root cause trail begins in May. 

 On May 13, Cosmos Labs opened a pull request, titled “fix: harden statedb balance and event amount handling.” Its description said the change would “guard StateDB balance subtraction against underflow” and make precompile balance-event parsing denomination-aware. 

 In the exploit path later confirmed by MANTRA , that combination could allow a contract to create an artificially inflated EVM-side balance and spend funds it did not legitimately control.

 The pull request merged into the main branch on May 15. 

 An independent researcher published a full write-up of the underlying exploit path on July 27 , in a piece titled " Printing Infinite Money on the Cosmos Blockchain ," reportedly after first reporting it through HackerOne.

 The backport to the release branches did not begin until Aug. 13 . 

 PR #1253 and PR #1254 were both merged into their respective release branches on Aug. 19, the same day Cosmos Labs shipped v0.7.2, whose release notes described the update as containing “important security fixes” and recommended a “coordinated upgrade.” 

 MANTRA's postmortem says the corresponding v0.6.2 release , the version relevant to MANTRA's own chain, was also published approximately 20 hours before the first drain .

 Neither release identified the balance-underflow vulnerability or explained its potential impact.

 At 07:16 UTC the next morning, a public pull request on Push Chain's fork of cosmos/evm precisely described the vulnerability and its exploit path , citing an independent Hacken audit and naming the vulnerable release tags, nearly 12 hours before MANTRA's first attack and roughly 16 hours before the chain went dark .

 That is the story the rest of the cluster tells. 

 MANTRA's own postmortem, published Aug. 28, confirms the same account : An unsigned-integer underflow in the balance-accounting layer of cosmos/evm, triggered by a specially constructed vesting account combined with a call through the staking precompile. 

 It was the defect the May guard was written to catch .

 Cosmos Labs' own postmortem, published the same day, named GHSA-7g4w-cg88-2cq2 , describes two chained defects, not one.

 An unchecked underflow lets a vesting account delegate more than its EVM-tracked spendable balance through the staking precompile , wrapping the balance to roughly 2^256. 

 That wrapped balance was then sent to a victim account , the burn address or the genesis multisig, producing an overflow that left the attacker holding the victim's balance and the victim holding zero. 

 Both fired inside a single, supply-neutral transaction , executed through a contract deployed at a precomputed address on top of the vesting account.

 The mechanism is visible in the chain’s own transaction history.

 MANTRA's postmortem lays out the mechanism transaction by transaction. 

 An attacker-controlled address submitted a CreateVestingAccount message at block 17,444,907 at 19:04:50 UTC on Aug. 20. 

 Seventy seconds later, a transaction in block 17,444,928 moved 600,000,035.56 MANTRA out of the null/burn address and into the attacker's wallet.

 A nearly identical sequence followed at 22:58:47 UTC: A second CreateVestingAccount message , then, fourteen seconds later, a transaction in block 17,449,159 draining 120,923,932.44 MANTRA from the genesis-era multisig .

 Cosmos Labs’ postmortem independently confirmed both transactions as MANTRA attack #1 and attack #2.

 Vesting accounts, it turns out, were the mechanism, confirmed in MANTRA's own account.

 The bug is no longer a mystery. A guard against it existed three months before MANTRA needed it, but the fix did not reach the relevant release branch, or the affected chains, in time. 

 Was the failure in the code, or in the release schedule that sat on the fix? 

## Mostly Gone

 The attacker sent 24 transactions during the incident , draining two compromised addresses, and, within minutes of each drain, [moving the proceeds out in fixed-size batches to a single exchange deposit address. 

 MANTRA halted the chain at block at 23:13 UTC , 14 minutes after the second drain. 

 By then, 682,966,951.64 MANTRA, 94.7% of everything taken, had already reached the exchange deposit address , moved in 15 scripted transfers spaced across roughly four hours.

 The halt froze only what was left behind : Approximately 37.96 million MANTRA, 5.27% of the total, still sitting in the attacker's wallet.

 Attacker's Wallet: 
 mantra13n9sk3p8x7tpq9adgxvzv9q0qev953mld0hwva 

 MANTRA's own postmortem values the total extraction at roughly $3.6 million , using the pre-incident spot price of $0.005 per token. 

 MANTRA fell 18.5% in the hours around the halt, from $0.005060 to a record low of $0.004126, while trading volume spiked nearly 600% as holders reacted to a chain going dark without an explanation attached. 

 MANTRA hotfix is released, v0.6.0-v8-mantra-6, at 02:28:46 UTC on Aug. 21 , hours before the final patch.

 MANTRA restarted on at 05:26 UTC on Aug. 22 running patched v8.4.0 , roughly 30 hours after the halt.

 Cosmos Labs' own postmortem gives a different time for the same milestone , 03:38:07 UTC, a discrepancy neither account resolves.

 There was no rollback, no alteration of the recorded chain state, and user balances were left exactly as they stood before the halt began. 

 The v8.4.0 release also restricted the attacker's account , immobilizing the remaining balance still sitting there. 

 As of Aug. 28, none of it, the frozen 5.27% included, had been recovered .

 The stolen funds never crossed a bridge or left MANTRA Chain for another network.

 But “on-chain” and “untouched” turned out to be two different claims. Almost all of the extracted funds reached an exchange-deposit address on MANTRA Chain before the halt caught up .

 Three more chains running the same underlying stack would not be so fortunate that week. 

 So what, exactly, separated a contained incident from a catastrophic one? 

## Everyone Else's Turn

 MANTRA's halt bought it time, but not an untouched ledger, most of the drained funds had already reached an exchange before the chain went dark. 

 Two days later, TAC and KiiChain halted too late to contain the funds. 

 On Aug. 22, the same vulnerability cluster drained 2,985,651,403 TAC from a single account and 148,326,583.15 KII across 18 repeated withdrawals from KiiChain .

 Rarma's forensic thread describes TAC's mechanism as the same vesting-account and staking-precompile pattern MANTRA's postmortem later confirmed .

 TAC has not independently confirmed that attribution.

 The attacks came two days apart but ended very differently: MANTRA's funds moved but stayed on MANTRA Chain, while TAC's and KiiChain's crossed bridges to other networks. 

 TAC's attacker bridged the tokens to BNB Chain in 95 seconds , roughly four hours before TAC's own halt took effect. 

 KiiChain froze 54.4% of the stolen KII on-chain ; most of the remainder was bridged out and sold for roughly 1.61 million BUSD.

 Nesa followed two days later . The project said it had identified malicious behavior on its L1, taken action to contain the impact, and taken its services offline while a software fix was applied.

 The extent of the loss was subsequently reconstructed from Ethereum-side bridge logs. 

 Cosmos Labs publicly released v0.7.2 on Aug. 19 , with the underflow fix described only as an “important security fix.” 

 It did not advise affected chains to halt immediately until Aug. 25 , six days later, when it told chains running versions earlier than v0.6.2 on the v0.6 branch or earlier than v0.7.2 on the v0.7 branch to halt and upgrade.

 Cosmos Labs first acknowledged an "ongoing security incident" on Aug. 24 , four days after MANTRA's halt and two days after TAC and KiiChain were compromised.

 KiiChain's postmortem, published Aug. 23, called the losses "avoidable" and directly criticized Cosmos Labs' disclosure process .

 Publishing a fix publicly before privately warning the chains running it, KiiChain wrote, "hands the vulnerability to anyone reading the commit." 

 KiiChain was not alone in that assessment. 

 Indie Developer De called the disclosure "negligent AF," pointing to the Aug. 19 release : “This release contains important security fixes. All chains should upgrade ASAP using a coordinated upgrade.” 

 The release included no public advisory and no main-channel announcement; the GitHub release itself described the change only as containing “important security fixes” and urged chains to upgrade using a coordinated upgrade.

 Protos likewise reported that MANTRA, TAC, KiiChain, and Nesa all appeared to be affected by the same Cosmos EVM vulnerability.

 MANTRA’s own postmortem adds a wrinkle to that account. It says MANTRA’s engineers reported both the vulnerability and the live exploit to Cosmos Labs directly, and that the security advisory sent to other Cosmos EVM chains went out only after that report.

 Cosmos Labs’ own postmortem independently confirms it : A war room was set up with MANTRA, and a private patch notice went out to known Cosmos EVM chains roughly two hours after MANTRA’s report, though that notice recommended upgrading, not halting. 

 The halt recommendation itself did not go out until roughly an hour after Cosmos Labs learned TAC had also been hit. 

 MANTRA wasn’t just another chain caught by a slow disclosure process; it was the one that triggered the wider response .

 That still sits uneasily next to KiiChain’s account , which blames Cosmos Labs for not warning affected chains fast enough and does not credit MANTRA’s report as the trigger.

 Both details can be true at once: MANTRA prompted the private outreach , and that outreach still was not fast enough to save TAC or KiiChain. 

 MANTRA, for its part, was already carrying weight before any of this began. 

 This is the same token that lost 90% of its value in April 2025 , and the exploit landed amid Inveniam Capital Partners’ proposed acquisition of MANTRA , a deal still targeted to close in the third quarter.

 MANTRA promised a postmortem on Aug. 23. 

 It finally arrived Aug. 28 , confirming the root cause but disclosing no fund recovery.

 Four publicly identified chains. One vulnerability cluster. A response that eventually became public, but only after the exploit had moved from MANTRA to TAC and KiiChain. 

 So who, exactly, gets to call this contained? 

 MANTRA wasn't beaten by a hacker's ingenuity. 

 It was beaten by an ecosystem that still doesn’t treat disclosure as part of the fix, publishing the patch without explaining its urgency and shifting to emergency halts only after the next chains were hit. 

 Saga lost roughly $7 million to a Cosmos EVM bug in January.

 Cosmos Labs shipped a permanent fix in March and marked the advisory as resolved.

 Seven months later, a compiled timeline placed the same shared module at the center of attacks affecting four more chains over five days.

 MANTRA’s own postmortem, published Aug. 28, confirmed which bug hit it : The same underflow the May guard was written to catch. 

 Cosmos Labs now says MANTRA’s report triggered its private response , and that its own initial assessment had wrongly concluded the vulnerability did not threaten production funds. 

 That explanation matters, but it does not erase the result: By the time the ecosystem moved to an immediate-halt posture, TAC’s funds had already crossed a bridge and KiiChain’s were already being drained. 

 By the numbers, 720,923,967.99 MANTRA, roughly $3.6 million by MANTRA’s own postmortem valuation , was extracted from two wallets.

 MANTRA reported that no user funds were exploited.

 No stolen tokens crossed a bridge to another blockchain , though 94.7% of them reached an exchange-deposit address before the halt caught up. 

 The network restarted roughly 30 hours later , and as of the postmortem, none of the extracted MANTRA had been recovered. 

 But clean is not the same as accountable. MANTRA moved fast enough to halt the chain and freeze the funds that remained during an active drain.

 It took more than a week to publicly confirm the bug that caused the incident, and, as of that confirmation, none of the extracted MANTRA, frozen or otherwise, had been recovered.

 Shared infrastructure holds only when disclosure is treated with the same urgency as the code itself. Nobody in this stack has proven that yet.

 This time, the warning eventually traveled. It just did not reach every chain in time.

 A chain can survive an exploit intact, confirm the exact bug that caused it, and still recover nothing for the people it affected. 

 Over a week later, what exactly does “contained” mean if nothing comes back? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

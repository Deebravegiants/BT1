# [H] Harmony exploit: On August 12, an attacker exploited flaws in Harmony’s legacy cross-shard verification path, and the protocol credited billions of ONE that no transfe

## Summary
Severity: High
Target: Harmony
Loss: $3,200,000
Published: 8/12/2026
Source: https://rekt.news/harmony-rekt2
Type: rekt-postmortem

## Details
## Harmony - Rekt

 Tuesday, August 18, 2026 Harmony - Rekt 

 read this article also in : 

 Harmony's own supply counter didn't blink. 

 On August 12, an attacker exploited flaws in Harmony’s legacy cross-shard verification path, and the protocol credited billions of ONE that no transfer backed , an anomalous mint Juiceberg had publicly flagged before Harmony said anything at all. 

 An initial four billion tokens surfaced within the hour, about 26% of the previously reported supply , while Harmony’s totalSupply endpoint did not reflect the new issuance, so every monitor relying on it was still reading yesterday’s supply. 

 Harmony's own August 17th trace put hard numbers on the spread : One wallet alone attempted 534 transfers of 5 billion ONE each in 106 seconds, 477 of which succeeded, moving 2.385 trillion ONE total, and a revised flow model reconciled almost 100% of the forged issuance to a wallet or service boundary.

 SlowMist's tracker lists the incident at $3.2 million , a third-party cash-out estimate that doesn't touch what the mint actually cost every other holder.

 This was Harmony's third major security failure in four years: A stolen bridge key in 2022 , a staking bug in 2023 , and now a legacy verification flaw the team is still fully accounting for. 

 ONE cratered to an all-time low of $0.0005735 before Harmony even had a name for what broke. 

 A patch stopped further minting within hours.

 Harmony has since published its rollback plan , Shard 0 held at block 92,730,034 and Shard 1 at block 94,978,278, both restored from replacement databases. Under that plan, every later block would be discarded and new blocks would resume at heights 92,730,035 and 94,978,279.

 Whether the rollback has actually been executed is separate from whether it has been decided, and the final mint total still has not been reconciled. 

 When a blockchain's own accounting system can't tell you how much of its currency exists, what exactly are exchanges pricing? 

 Credit: Harmony , SlowMist , Juiceberg , Matthew Barrett , Tech Times , ZachXBT , CertiK 
 Juiceberg fired first , publicly, before Harmony said a word. 

 On August 11th, on-chain analyst Juiceberg laid out the initial figures : Roughly 4 billion ONE minted through empty blocks, about 26% of the previously reported supply, and 2.8 billion routed toward exchange addresses as the price fell.

 The same post flagged a second problem that would shape the story for days after , Harmony's totalSupply endpoint wasn't reflecting the unauthorized issuance.

 Harmony didn't respond for almost three hours.

 The official account quote-posted Juiceberg directly, offering coordination with exchanges, a patch in progress, rollback options under evaluation . No figure confirmed. No cause named. 

 Within the hour, Harmony followed with four wallet addresses , asking every exchange watching to freeze anything tracing back to them. 

 Harmony paused bridge.harmony.one as a containment measure . Its own incident report puts the emergency patch , v2026.1.1 , at 06:30 UTC on August 12th, built around pull request #5101 , deployed after the bridge was already down, not before.

 The patch stopped further unauthorized minting.

 Then came the part no patch could touch. ZachXBT said he wouldn't be tracing this one and argued nobody else should for free , pointing back to how Harmony had treated the people who helped recover funds after the 2022 Horizon Bridge hack, freezes that led to law-enforcement seizures, acknowledged, by his account, highlighting that they got nothing more than a “good job. ”

 Hours later, Harmony's own numbers finally caught up to the scale of it : 10,288 transfers traced across 409 wallets, hundreds of suspicious exchange deposits flagged, 53% of validators patched within four hours of release.

 The team thanked its validators . It still hadn't said what broke .

 If the official response couldn't outrun the exploit, what exactly was being protected, the funds, or the timeline? 

## Credit Without Debit

 Harmony’s cross-shard design was supposed to let value move among its four shards through a native , receipt-based mechanism rather than an external bridge. 

 Harmony supports cross-shard transactions through a receipt-based, asynchronous communication mechanism designed to achieve eventual consistency , so no double spending is possible between shards. 

 The destination shard is supposed to verify the receipt and proof before processing it. In Harmony’s intended design, that receipt-based mechanism was meant to prevent cross-shard double spending .

 Harmony’s cross-shard receipt-verification logic allowed valid receipts to be processed multiple times .

 Before IsCXMerkleProofReplayFixEpoch , Harmony’s legacy replay check derived a receipt’s spent-marker key from CXMerkleProof.ShardID and CXMerkleProof.BlockNum.

 Because ValidateCXReceiptsProof did not bind those fields to the signed source-block header for those epochs , an attacker could alter them without invalidating the header signature, making an already processed receipt appear new. 

 While the Header itself could not be altered without failing VerifyHeaderSignature, the Merkle-proof identity fields were unauthenticated. By modifying those identifiers, an attacker could make processed receipts appear new. 

 An attacker could take an already processed cross-shard receipt and resubmit it with those identifiers altered . Each altered submission would produce a different spent-marker key, causing IsSpent to return false and making the receipt appear new.

 When that happened, ApplyIncomingReceipt credited the destination shard without a corresponding debit on the source shard.

 The result was native ONE inflation in empty, zero-gas blocks: The state root changed despite the absence of ordinary or staking transactions.

 Harmony found a second issue in pre-staking quorum verification: uniformVerifier.IsQuorumAchievedByMask used the size of the full committee, len(mask.Publics), instead of counting only validators enabled in the signer bitmap. 

 Under that vulnerable logic, an empty signer bitmap combined with an identity , or all-zero, aggregate BLS signature could satisfy quorum for any pre-staking-epoch committee. 

 A nil mask was not rejected; the affected path was used to verify pre-staking-era committees , including source headers attached to old cross-shard receipts.

 Harmony’s report leaves one question open: Whether the exploit relied solely on the cross-shard receipt issue or also leveraged the pre-staking quorum-verification flaw.

 Harmony patched both issues in mainnet release v2026.1.1 , included in PR #5101. 

 Which vulnerability, or combination of vulnerabilities , the attacker actually relied on remains unconfirmed.

 Two checks failed either way. One let a used receipt pass as unused. The other meant a pre-staking-era header with no enabled signers could still pass quorum.

 Neither required breaking a single cryptographic primitive, both just needed nobody to check what the numbers actually proved. 

 If a chain can't tell a header with no enabled signer record from one with genuine validator approval, what exactly was consensus protecting? 

## The Accounting Gap

 Whatever the "already spent" check was supposed to catch, this is what got through instead. 

 Two mints, two transfers, four wallets flagged for freezing, all inside a few minutes, and every address involved sits in public record. 

 Mint Recipient 1 - (1,000,000,000 ONE): 

 one17u300a40ll5wphd8kj5hktryhdjq3ml9f4phy4 

 Mint Recipient 2 (3,000,000,000 ONE): 
 one1a5hur07z5vtvzhr35zkw8tfqedemkz8t88xgd7 

 Four billion tokens minted across two empty blocks.

 The second wallet didn't sit still. It moved the funds out in two hops, first to a second wallet within ninety seconds, then that wallet forwarded nearly all of it to a third within three minutes.

 Transfer Transaction 1 (2,800,000,000 ONE): 0xf3d4e8b12479ae14cd5eae973a5f61b07d567b142a6ca1385471d5c288242c7f 

 Transfer Transaction 2 (2,799,999,999.99183949 ONE): 0x9a756ef9f95a4c737b3c7e87f04419e9391f226c631ff7b81c401619b0a4d678 

 Nearly the entire balance moved again under three minutes later , at 01:05:24 UTC. 

 The four wallets Harmony asked every exchange to freeze are as follows … 

 Freeze Wallet 1: 
 one1uap8dx2z0qsjxqthm5flgcxkeepsz3gsrghnfn 

 Freeze Wallet 2: 
 one17u300a40ll5wphd8kj5hktryhdjq3ml9f4phy4 

 Freeze Wallet 3: 
 one1a5hur07z5vtvzhr35zkw8tfqedemkz8t88xgd7 

 Freeze Wallet 4: 
 one1h56hkxmua0uzfv07fu04cudvtrl35u96pq47vy 

 That is the confirmed first wave, four billion ONE, and it is only one of two figures in Harmony's accounting. 

 Its incident report says it is still reconciling that first-wave measurement with a reconstruction of 3,010,000,100,000 ONE across six forged cross-shard transactions into four exploiter wallets. 

 Harmony stated that the 4,000,000,000 ONE figure represents the initial wave , whereas the 3,010,000,100,000 ONE figure reflects the full forged cross-shard issuance into four exploiter wallets.

 CertiK independently reported an anomaly exceeding 3 trillion ONE across six abnormal blocks.

 A protocol can describe its own exploit at two different sizes at once.

 On August 17th, Harmony published a later flow reconstruction. One forged-mint wallet attempted 534 transfers of 5 billion ONE each in 106 seconds, of which 477 succeeded, moving 2,385,000,000,000 ONE from one wallet . 

 That equals about 79% of Harmony's provisional 3.0100001 trillion ONE full-issuance reconstruction . 

 Harmony said its earlier flow model routed more than 99.9% of forged ONE to a wallet or service boundary , while a later model reconciled almost 100% across those boundaries and transaction fees at the same cutoff.

 It checked the traced transfers against block data , transaction receipts, and balances through Shard 0 block 92,805,850

 But traceability is not attribution or recovery. Harmony says “traceable to a wallet or cluster” means it can follow forged ONE to a wallet, pool, contract, exchange, bridge, validator, or service - not identify the person controlling it; a cluster or service wallet may represent many unrelated users. 

 Harmony also distinguishes traceability from what is safely burnable : Once forged ONE entered a CEX wallet, DEX pool, LP position, bridge contract, staking position, or other shared balance, burning the full traced amount could take unrelated funds or damage the service

 The initial four billion ONE wave alone represented roughly a quarter of Harmony's previously reported supply .

 A cash-loss figure cannot capture the dilution borne by holders, or distinguish coins sold, frozen, pooled, or ultimately erased by rollback. 

 If Harmony can trace nearly all of the route but cannot infer control from an address, or recover the funds without risking harm to unrelated users, what exactly does "traceable" mean? 

## Undoing What's Already Gone

 By the time Harmony began preparing a rollback, Shard 0 had already been halted. 

 Harmony said it stopped at block 92,753,555, 12:32:54 UTC on August 12th , to facilitate the rollback, and that the official RPC could return a 502 error as a result. 

 A rollback preserves a checkpoint and discards all subsequent blocks and their on-chain history.

 Harmony explicitly says all blocks after the checkpoints, including regular transactions , will be discarded.

 Harmony's August 13th incident report identified block 92,730,034, timestamped 23:25:37 UTC on August 11th , as the candidate rollback point, one block before the first forged cross-shard activity the report itself flags.

 By August 17th, that candidate had become the plan, chosen as a one-block safety buffer. 

 Harmony said it would retain Shard 0 at block 92,730,034 and Shard 1 at block 94,978,278, both at that same timestamp , then create new blocks at heights 92,730,035 and 94,978,279. 

 Client v2026.1.2 rejects the listed problematic block hashes as part of the recovery procedure.

 This isn't a targeted deletion of the attacker's transactions. It's a full replacement of chain history, every post-checkpoint block removed, whether or not it involved forged ONE .

 Harmony says it considered a targeted burn, a blacklist, selective transaction replay, a token migration , and its own built-in revert tool before choosing this.

 It rejected the burn because forged ONE had already spread into shared balances, the blacklist because it would leave the forged supply in place while potentially catching unrelated wallets , and selective replay because changed chain state means a transaction can now produce a different result, leaving no fair rule for choosing what to restore. 

 The cost is measurable. Harmony's archive from Shard 0 blocks 92,730,035 through 92,871,662 runs 141,628 consecutive blocks , 109,126 regular transactions, and 315 staking transactions, all of it set to be absent from the replacement chain history. 

 Only 22 regular transactions appeared to carry no obvious dependency on anything else , and Harmony says even those aren't safe to restore.

 That scale matters because a rollback cannot itself resolve forged ONE that had already reached third-party services before the halt. It can replace Harmony's on-chain history, but it cannot directly unwind activity at exchanges, bridges, or other external services.

 Harmony has not publicly identified the exchanges involved.

 As of this writing, Harmony says it plans to proceed with the rollback , but it hasn't happened yet.

 The bridge remains paused and Harmony says the emergency patch was deployed and activated after the validator threshold was met. 

 If removing the forged issuance requires discarding more than 109,000 ordinary transactions, whose ledger is actually being protected? 

 Three times in four years, Harmony has given the market a new reason to question ONE's security record. 

 In 2022, attackers compromised enough Horizon Bridge signing authority to drain roughly $100 million in assets. 

 In 2023, a staking-system bug improperly created about 146.28 million ONE .

 This time, Harmony says a flaw in its legacy cross-shard receipt-verification path let valid receipts be processed repeatedly , crediting a destination shard without a corresponding source-chain debit.

 The resulting state changes occurred in empty , zero-gas blocks, no ordinary or staking transactions, but a changed state root.

 Harmony's provisional reconstruction identifies six forged cross-shard transactions into four exploiter wallets.

 It plans a rollback down to specified block heights, but that doesn't make the cost disappear : more than 109,126 regular transactions are set to be absent from the replacement chain history, while Harmony has not publicly identified the exchanges involved.

 A network built to coordinate activity across shards found its weakest point in the logic meant to verify that coordination. 

 If sharding is designed to make trust invisible, what catches it when trust breaks? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

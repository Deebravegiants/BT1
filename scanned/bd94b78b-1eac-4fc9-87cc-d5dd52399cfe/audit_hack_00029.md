# [H] Aztec Bridge exploit: On June 14th, an attacker drained $2.28 million from a deprecated Aztec Connect contract that Aztec Labs had wound down in 2023 and handed back the ad

## Summary
Severity: High
Target: Aztec Bridge
Loss: $2,198,000
Published: 6/17/2026
Source: https://rekt.news/aztec-bridge-rekt
Type: rekt-postmortem

## Details
## Aztec Bridge - Rekt

 Wednesday, June 24, 2026 Aztec Connect - Aztec Labs - Rekt 

 read this article also in : 

 On June 14th, an attacker drained $2.28 million from a deprecated Aztec Connect contract that Aztec Labs had wound down in 2023 and handed back the admin keys on in 2024 , exploiting a mismatch between the ZK proof verification layer and the L1 settlement logic. 

 The contract was immutable. There was nothing to patch and nothing to recover. 

 Three days after the first drain , on June 17th, the same deprecated bridge stack handed someone else $2.198 million.

 Not the same contract, not the same flaw, not the same entry point, but it did have the same foundational assumption: That a ZK proof connecting two independent witnesses was actually constraining something.

 The attacker funded a fresh wallet with 0.134 ETH from HitBTC , called escapeHatch() on a deprecated Aztec 2.0 rollup contract that hadn't been a maintained product since 2022 , and walked out with 1,158 ETH, 150,000 DAI, and 0.4696 renBTC across three transactions in thirty-seven minutes.

 The escape hatch was designed as the last resort, the function users could call to force their own funds out if the sequencer went dark . It verified ownership with a ZK proof. 

 The exploit came from a mismatch between the verified rollup transaction set and the L1 settlement processing boundary. 

 numRealTxs was not effectively bound to the transaction set enforced by the proof , so the proof path and the L1 settlement logic interpreted the transaction list differently.

 Aztec Labs held no admin keys. The contract was immutable.

 The circuit that enabled the flaw had been removed from the codebase years earlier, but the deployed verifier still contained the old escape hatch verification key. Proofs built against the old circuit remained valid on-chain. 

 When a protocol removes a vulnerable circuit from its codebase but leaves the deployed verifier intact, who owns the gap between what the code says now and what the contract still accepts? 

 Credit: Aztec Labs , Peckshield , Blocksec Phalcon , thisvishalsingh , CertiK , MistTrack , L2Beat , Specter , TrustSec , Defi Edward 
 thisvishalsingh was first on the scene, the evening of June 17th , three hours after the drain had settled on-chain. 

 The read was careful and restrained : A call to escapeHatch() on the Private Rollup Bridge contract , 1,158 ETH to the caller, no reverts, no unusual internal flows, the proof package went through.

 The on-chain trace looked surgical , 0.00009 ETH in gas, a single RollupProcessed event for rollupId 4487, and a balance that had just become zero.

 The open question, flagged explicitly, was whether the proof had represented real ownership or had passed through a gap in the verification logic .

 The answer would take until the following morning. 

 CertiK confirmed the drain later that night , naming the attacker address and estimating the loss at roughly $2.15 million. 

 Their follow-up thread surfaced an early mechanical observation : Within the escape hatch's call window of 240 calls per 4,800 blocks, the attacker had submitted proofData with rollupSize and numTxs set to zero at the proof header while real withdrawal parameters sat further into the data.

 Verification pulled the zeroes .

 Execution, hardcoded to process at least one transaction at line 512 , pulled the withdrawal values.

 The two reads looked at different parts of the same calldata and reached different conclusions. 

 PeckShield confirmed the full asset picture shortly after midnight : 1,158 ETH, 150,000 DAI, 0.4696 renBTC, for an estimated total of approximately $2.165 million at the time, the attacker wallet, originally funded with 0.134 ETH from HitBTC . 

 BlockSec Phalcon followed with all three attack transaction hashes and noted the connection to the June 14th exploit , two separate deployments, two separate entry points, the same underlying class of proof-binding gap.

 Aztec Labs posted in the early hours of June 18th , with a brief statement describing the target as "a deprecated Aztec payments product from 2021," confirming the contract was immutable and beyond their control, and separating the incident cleanly from the June 14th Aztec Connect drain .

 The Aztec Foundation followed one minute later with the same ring-fencing : No connection to the current Aztec Network, no connection to the AZTEC ERC-20 token.

 Both posts were factually accurate and said almost nothing about how the money had actually been taken.

 The full technical account, the circuit binding gap, the fake Merkle tree, the two independent witnesses with no equality constraint between them, came from BlockSec Phalcon the following morning and Aztec Labs' own incident report , and is covered in the next section. 

 When the first alerts name the attacker and the amounts but the protocol's own statement omits the mechanism entirely, what does the public record actually contain in the hours that matter most? 

## The Unbound Root

 To withdraw from Aztec 2.0, a user had to submit a ZK proof showing that the funds existed in the private ledger, had not already been spent, and belonged to the claimant . 

 The verifier checked that proof against a verification key generated from the circuit, while the settlement contract trusted the verifier to establish ownership and then executed the withdrawal . 

 The escape hatch circuit used old_data_root in two places.

 One instance was fed into the join-split circuit at line 33 as the root used for note membership checks.

 A second instance was exposed as a public input at lines 50 and 88 , then compared in Solidity against the live on-chain state via require(oldDataRoot == dataRoot).

 The circuit did not enforce that those two values were the same. 

 That missing equality constraint was the exploit. The attacker built a fake Merkle tree containing fabricated notes , proved membership against that fake root, and supplied the real on-chain root as the public input. 

 The circuit accepted the proof , the Solidity check passed against the genuine root, and the withdrawal executed.

 Aztec Labs' incident report said the result was visible on-chain : The attacker's proof stated deposit = 0, withdraw = 1,158 ETH, and the notes cited as the source of those funds were fabricated, a combination that cannot occur in a legitimate proof.

 The flaw resided not in the verifier's execution but in what the verification key encoded : A circuit that never required its two uses of old_data_root to match. 

 The shared cryptographic trusted setup was not compromised. 

 The vulnerable escape hatch circuit had already been removed from the codebase in PR #402 , but the deployed verifier contract still contained the verification key generated from that circuit .

 The repository had moved on. The chain had not.

 Proofs built against the old circuit remained valid on-chain, because the key that accepted them was still there. 

 When the code says one thing and the deployed verifier still accepts another, which one is the contract actually running? 

## Three Clean Exits

 The attacker funded a fresh wallet with 0.134 ETH for gas at 18:21 UTC on June 17th . Thirteen minutes later, the first transaction cleared . 

 At 18:34 UTC, 1,158 ETH left the contract in a single call through the escape hatch , the overwhelming majority of what would be taken. 

 Fifteen minutes later, at 18:49 UTC, a second transaction drained 150,000 DAI .

 One minute after that, at 18:50 UTC, a third transaction swept ~0.47 renBTC 

 From gas funding to final drain, the full operation took roughly 37 minutes .

 The three attack transactions, in order: 

 1,158 ETH Attack Transaction: 0xab306cd2184d23b6ba3e151b10b3b9a0b81f211cc16f4f3b0c79f0b17a59c2b5 

 150k DAI Attack Transaction: 0x5c196c37a109d74c9797254287a0331f30e0daa637af241bd28fdc43774705c3 

 0.46963295 renBTC Attack Transaction: 0x9e1d6ab7c20ae235409d7dd3a9cd47c04f07293585b3498b8beed82d6f6b03ca 

 The ETH was worth approximately $2.04 million at the time of the exploit. 

 The DAI was worth $150k . 

 The renBTC figure of roughly $7,000 was an upper bound per Aztec Labs' incident report , which noted that renBTC is a deprecated and depegged asset whose real value was likely far lower.

 Total taken in the primary attack: Approximately $2.197 million.

 The attacker's wallet was originally funded by HitBTC .

 The attacker consolidated primary funds at the EOA, with partial ETH distributed to two holding addresses identified by MistTrack . 

 Approximately 300 ETH moved to one address and 56 ETH to a second, per Aztec Labs' incident report . 

 Attacker EOA: 
 0x6952d9246e9aFE8B887B2877225163436F78E97F 

 Victim Contract (Aztec: Private Rollup Bridge): 
 0x737901bea3eeb88459df9ef1BE8fF3Ae1B42A2ba 

 Holding Wallet A: 
 0x15930a0fef3421f48c6553b5691682cc1b22edb3 

 Holding Wallet B: 
 0x33d6a0d9bc210e823e043d604179cd844eb467df 

 The following morning, approximately 13.5 hours after the primary attack, a separate actor swept the residual 0.76 ETH remaining in the contract via the operator path rather than the escape hatch, bringing the secondary take to roughly $1,300 . 

 Second Attacker EOA: 

 0xb6f89d12Ff9A9e394f40B701Ac46428DE0d1bEa5 

 Secondary Attack Transaction: 

 0x389bce3dad78c09900cb4c9e72397a73b39b8217ae37ef264f3439046737cb0c 

 Total amount stolen by the 2 attackers: $2.197 million

 That path was accessible because a default Anvil/Hardhat developer test account had been registered as an authorized operator during the 2024 decommissioning process.

 The attacked contract is almost empty : ~$50 left as of publishing time.

 Two attackers, three transactions for the first, one for the second, and a contract that had been sitting on-chain, unmonitored, since 2022 with nothing left to give . 

 What does it mean for users whose funds were still in a deprecated contract when the sequencer stopped running and the only exit was an escape hatch built on a flawed circuit? 

## No Keys Left

 Aztec Labs published a full incident report in the days following the exploit , confirming the root cause, laying out the timeline, and naming Groom Lake as its incident response provider, engaged to coordinate fund blocking across exchanges. 

 No compensation mechanism was described . No recovery path existed. The contract was immutable, and Aztec Labs had renounced all administrative control in April 2024 . 

 There was nothing left to do but document what had happened.

 That April 2024 key revocation matters because it came after a year of supported exits and public reminders urging remaining users to withdraw : Aztec Labs formally relinquished all administrative roles and renounced all upgrade authority on-chain.

 That decision is part of the same decentralization posture reflected in the current Aztec Network’s L2Beat Stage 2 rating , one of the highest available for rollups. Few L2s reach it.

 The same architectural discipline that earned that rating meant that when the escape hatch circuit flaw surfaced three years after the product was wound down, there was no key to reach for and no upgrade to push. 

 Onchain investigator Specter put the criticism plainly : If a contract is no longer being used and there is no team actively maintaining or monitoring it, the right move is to withdraw the funds and shut it down properly rather than leave it waiting to be exploited. 

 Fran, an Aztec ecosystem community member and Foundation contributor, offered context in response : Aztec Connect was wound down around three years ago. Most users withdrew their funds, but some money was still sitting there, likely from people who lost access to their wallets or never bothered to claim it. Last week, someone stole about $2 million from those remaining funds, and another roughly $2 million now appears to have been taken. This was an old contract that Aztec Labs does not control, and it is not connected to Aztec Network or $AZTEC. The broader risk applies to legacy smart contracts that are no longer actively monitored, maintained, or battle-tested.

 But that debate does not fully capture the technical point: The immutability and key revocation that made the contract trustless also left Aztec Labs with no administrative way to intervene.

 The escape hatch circuit had been removed from the codebase in PR #402 , but the EscapeHatchVk it generated remained deployed in the verifier.

 In other words, responsible deprecation covered the operational layer, but it did not change what the verifier would still accept. 

 The two Aztec exploits in three days, the June 14th Aztec Connect drain and this one, combined for more than $4 million in losses across deprecated contracts the current team had no ability to intervene in. 

 The loss total was still growing when the follow-on sweep added its $1,300 the following morning .

 Independently, it raises a harder question: If a white hat discovers a critical flaw in a fully disowned project, what can they actually do?

 TrustSec framed the harder question after the Aztec incident : What should a white hat do upon finding a critical vulnerability in a fully disowned project? 

 Disclose it publicly and risk alerting every bad actor watching the feed . Attempt a quiet recovery alone and face frontrunning bots, legal exposure, and execution risk. Or bury it, knowing the next person to find the same gap may not be weighing the same options.

 None of those paths were clean, and none offered an easy answer. 

 When a protocol revokes its keys, completes its deprecation, and earns one of the highest decentralization ratings available, then watches a flawed verification key drain the last of its users' funds, what exactly did responsible sunset look like from the inside? 

 Two deprecated contracts, two separate circuit-level flaws, more than $4 million gone in three days, and a team that had done everything the industry considers responsible : Gave users a year of notice, ran the exit infrastructure, revoked the admin keys on-chain, and walked away cleanly. 

 That last part is what makes this harder than most exploits to assign. 

 Defi Edward's question cuts to the center of it : How many L2s talk decentralization but never actually revoke their admin keys?

 Aztec did revoke them . The contract became trustless. And trustless, in this case, meant there was no one left to call when the verifier kept accepting proofs from a circuit that had been removed from the codebase years earlier.

 The escape hatch was supposed to be the safety net, the mechanism that let users exit when every other path closed.

 The flaw wasn't in the idea of an escape hatch. 

 It was in the binding gap behind the escape hatch: The circuit treated the same root as two separate values, and nothing forced them to match. That let a proof pass even when the tree being proven against was not the tree the contract was checking on-chain. 

 Aztec 2.0 was deprecated in 2022. 

 It sat on-chain for roughly four years after that, with source code public, balances visible, and the verification key intact, until someone read the circuit carefully enough to find the gap.

 The cryptography didn't fail. The sunset did. 

 When every good-faith effort at responsible deprecation still ends with users losing funds to a flaw nobody caught, what exactly does the industry owe the people whose money was still inside when the door finally closed? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

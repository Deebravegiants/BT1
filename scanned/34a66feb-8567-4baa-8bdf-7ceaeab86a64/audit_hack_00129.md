# [H] Hyperbridge exploit: 1 billion DOT tokens minted , $2.5 million in losses , one missing line of code

## Summary
Severity: High
Target: Hyperbridge
Loss: $2,500,000
Published: 4/13/2026
Source: https://rekt.news/hyperbridge-rekt
Type: rekt-postmortem

## Details
## Hyperbridge - Rekt

 Friday, April 17, 2026 Hyperbridge - MMR - Proof Verification 

 read this article also in : 

 1 billion DOT tokens minted , $2.5 million in losses , one missing line of code. 

 Initially reported as a $237k loss, Hyperbridge revised that figure to $2.5 million , citing two separate attacks and users who swapped into artificially cheap DOT after the pools were drained . 

 Hyperbridge built its entire identity around a single promise : Cryptographic proofs, not human committees, would keep its bridge secure.

 No multisig. No validators. No trust.

 Just math, math that the Polkadot ecosystem backed with a $5.3 million seed round , and, six weeks earlier, a Polkadot OpenGov vote to hard-cap DOT supply at 2.1 billion tokens in a bid for monetary credibility.

 On April 1st, Hyperbridge announced that the Lazarus Group had drained $37 million - a joke, before linking to a since deleted blog post explaining "Why Hyperbridge Can't Be Hacked."

 Founder Seun Lanlege had said as much in a December 2025 interview : "Unless the cryptographic libraries themselves fail, the proofs cannot be forged." 

 Twelve days later, the cryptographic library failed. The proofs were forged. 

 The April 1st post and tweet were since removed. What replaced them was a real exploit announcement that opened, without a trace of irony.

 One missing bounds check, a single require statement that was never written, let an attacker submit a fabricated proof, seize admin control of the bridged DOT token contract on Ethereum, mint a billion tokens out of thin air , and walk away with everything the liquidity pool had to offer.

 The attacker didn't outsmart the cryptography. They found the place where the math stopped and the Solidity began. 

 When a protocol's security guarantee lives or dies on a library nobody fuzz-tested, who exactly was minding the proof? 

 Credit: CoinTelegraph , techcabal , coindoo , Techparley , CertiK Alert , Zilayo , PeckShield , BlockSec Phalcon , Arkham , Hyperbridge , Polkadot , DLNews , Stepan Chekhovskoi , SpecterAnalyst , DEGEN NEWS , AInvest , Arkham , Range 
 Zilayo fired first early on April 13th - No preamble, no hedging - just admin changed to the attacker's contract, 1 billion DOT minted. 

 PeckShield followed 21 minutes later , amplifying it to a wider audience.

 CertiK followed minutes later with the transaction hash and the mechanism in plain terms.

 The attacker had slipped through a forged message , changed the admin of the Polkadot token contract on Ethereum, minted a billion tokens, and cashed out approximately $237,000 .

 One sentence. Done.

 BlockSec Phalcon came next with more detail , initially framing it as an MMR proof replay vulnerability caused by missing proof-to-request binding - a valid description of the symptom, though the precise root cause would sharpen in a second post. 

 Their alert named the HandlerV1 contract specifically , listed six attack transactions, and noted what the attacker had actually done: Changed the admin of the DOT token, then used that admin access to mint. 

 Arkham tracked the wallet in real time . The attacker's address was already moving funds by the time the first alerts landed.

 Primary Attacker Address on Arkham: 
 0xc513e4f5d7a93a1dd5b7c4d9f6cc2f52d2f1f8e7 

 Hyperbridge went quiet for hours. When the team did speak, they opened with "Security Update!" , with the replies turned off. 

 Maybe the April Fools Joke did not go over too well, given the irony. 

 Polkadot moved faster than Hyperbridge did. Their official account clarified that native DOT , and all parachains were fully secure and unaffected.[

 Parity Technologies, a Polkadot developer, told DL News the roughly same thing : No vulnerability in Polkadot's protocol, consensus, or audited core code.

 Hyperbridge's official statement acknowledged $237,000 in losses , that figure would become $2.5 million three days later . Bridging was paused. The team said it was working with security partners to trace and recover funds .

 A protocol that spent two years telling the industry it had solved bridge security had just been handed the bill for the one assumption nobody checked. 

 How does a library built by the same team that built the bridge end up with an untested edge case at the center of its security model? 

## Forged in Plain Sight

 Hyperbridge's cross-chain messaging worked like this: A user sends a request on Polkadot, a relayer carries a proof of that request to Ethereum, and the HandlerV1 contract on Ethereum validates that proof before dispatching any action. 

 The entire security model rested on that validation step. If the proof passed, the message was treated as legitimate. If the message was legitimate, its instructions were executed, including instructions that could reassign who controlled a token contract . 

 Those instructions landed in TokenGateway, the contract responsible for minting and burning wrapped assets .

 The attacker's goal was simple: Make a forged message pass as legitimate. Everything else followed from that.

 The attacker submitted a ChangeAssetAdmin request targeting the bridged DOT token contract .

 The core of the exploit lives in one function call : HandlerV1.handlePostRequests, the handler that processes incoming cross-chain messages.

 Its job : Fetch a Merkle root, validate that the message is included in that tree, then dispatch the action if the proof holds.

 The attacker needed step two , to validate that the message is included in that tree, to pass for a message they had fabricated from scratch . 

 Here's what they actually submitted : 

 MerkleMountainRange.VerifyProof(
root: 0x466dddba7e9a84a0f2632b59be71b8bd489e3334a1314a61253f8b827c9d3a36, proof: [0x466dddba7e9a84a0f2632b59be71b8bd489e3334a1314a61253f8b827c9d3a36], leaves: [{ k_index: 0, leaf_index: 1, hash: 0xb870f0ca...318a99d }],
leafCount: 1
) 

 proof[0] == root. That's not an accident.

 CalculateRoot(), the function underneath VerifyProof(), has an early exit for single-leaf trees .

 When leafCount == 1, leaves.length == 1 , and leaves[0].leaf_index == 0, it returns the leaf hash directly. A fast and clean path.

 The attacker set leaf_index to 1 instead of 0. One digit off. That single change bypassed the early exit entirely and sent execution down the general path , where the function looked for leaves within each subtree. 

 With an out-of-bounds leaf_index, no leaves fell within any subtree, so instead of incorporating the leaf into the calculation, the function reached for the next item in the proof array and pushed it directly onto the peak roots stack. 

 The function returned proof[0] . The attacker had set proof[0] equal to the expected root. Computed root matched expected root. Verification passed.

 The attacker's actual leaf hash was never used in the calculation at all. It was decorative. The message was entirely fabricated. The verifier accepted it without question.

 ChangeAssetAdmin executed.

 Admin and minter rights for the bridged DOT token contract transferred to: 0xc513e4f5d7a93a1dd5b7c4d9f6cc2f52d2f1f8e7 

 The attacker didn't arrive unprepared.

 A contract containing the core mint and swap logic had been pre-deployed days earlier : 
 0x31a165a956842aB783098641dB25C7a9067ca9AB 

 The exploit transaction itself deployed a minimal proxy as the direct attack vehicle : 
 0x518ab393c3f42613d010b54a9dcbe211e3d48f26 

 By the time the forged proof was submitted, the exit was already built.

 From there, minting a billion tokens was a formality, and dumping them for 108.2 ETH was simply a matter of how deep the pool ran. 

 It ran to $237,000. That was the floor. Not the ceiling, the entire available depth . 

 One bounds check, require(leaf_index < leafCount), would have reverted the transaction before any of this happened .

 It was never written . The library flagged no invariant requiring it.

 The calling code validated nothing before passing untrusted input into a security-critical function.

 Neither layer caught what the other assumed the other was handling.

 Blocksec Phalcon's final root cause update put it plainly : The verifier does not enforce leaf_index < leafCount.

 If an attacker submits leafCount = 1 and leaf_index = 1, CalculateRoot() never incorporates the request commitment into root computation, the proof passes for arbitrary request content, decoupled from the message it was meant to authenticate . 

 When a library is both authored and consumed by the same team, who owns the assumption that inputs will be valid? 

## The Number That Kept Changing

 The timeline that Hyperbridge's official statement didn't tell. 

 There was more than one attack and more than one attacker. 

 The first attack got less coverage. According to SpecterAnalyst , it also walked away with more.

 According to on-chain investigator SpecterAnalyst , Hyperbridge's TokenGateway contract was hit for 245 ETH, approximately $570k, before the main attack made headlines.

 The exit was methodical : Funds split into 16.39 ETH per wallet across 15 addresses, then deposited into Tornado Cash. No negotiation. No bounty contact. Just a clean split and a vanish.

 Hyperbridge's TokenGateway Contract: 

 0xFd413e3AFe560182C4471F4d143A96d3e259B6dE 

 Attacker’s Address: 

 0xc0564bBa9Ba5A9bE95AE866429F936012E1bF143 

 Contract Used in Attack: 
 0xCcd363E1A098558b17431b934fffac9906855a5d 

 Attack Transaction: 0xeff151ef58d57d6523874a7b97344fcd1ce3c7c6880cfc26a93da17f82062d59 

 This earlier drain appears to have been a separate attack, not the one tied to the HandlerV1 vulnerability . 

 The headline exploit followed at 03:55 UTC on April 13 . 

 The same TokenGateway contract managed four assets, all hit in the same transaction. 

 Beyond minting the 1 billion DOT , the attacker also minted roughly 999 billion ARGN tokens and targeted MANTA and CERE .

 ARGN Transaction: 

 0xb28ab9526e1538bdb7a26ec8485d055f9e417620c72a2f4de0f42234b5f8ac09 

 The rest of the on-chain picture is as follows… 

 HandlerV1 Contract (vulnerable): 

 0x6C84eDd2A018b1fe2Fc93a56066B5C60dA4E6D64 

 Hijacked DOT Token Contract: 

 0x8d010bf9c26881788b4e6bf5fd1bdc358c8f90b8 

 Primary Attacker: 
 0xc513e4f5d7a93a1dd5b7c4d9f6cc2f52d2f1f8e7 

 Primary Attack Transaction (1 Billion DOT Minted): 0x240aeb9a8b2aabf64ed8e1e480d3e7be140cf530dc1e5606cb16671029401109 

 Additional Attack Transactions: 0xb93aab835e4002f7d46b63e37a156c78abd1d9256df094d63321deeb514a0634 0x6f1efcde4a52db999c8cd233364d889292ae5ba357d9f2ead3dd3774010a0808 0x743f4bdb67df7e6db57346e557f94ded8d7f85e854040963b7f345545e227125 0xb80c7d4cde034689eb9aa42f0d28aa01d12e233e3805a7c8888ed871b7443c3a 0xb28ab9526e1538bdb7a26ec8485d055f9e417620c72a2f4de0f42234b5f8ac09 0xfa23fb22cc8ff10518e561817dea838d3232f7573fd90bd81fd7a30a9161b6f6 

 The combined notional value of tokens minted ran into the billions. Shallow Ethereum liquidity pools prevented the attacker from realizing more than a fraction of that sum. 

 The original headline number was $237k. The full picture is less tidy. 

 Same exploit. Same window. Two different attackers.

 The main attacker walked away with $237K, limited only by what the limited liquidity pool could absorb before collapsing to near zero.[

 According to SpecterAnalyst, a separate actor had already taken 245 ETH through the same door before the DOT mint made headlines.

 Three days later, Hyperbridge revised its loss estimate to approximately $2.5 million , a figure that includes not just funds extracted by the attacker, but losses from incentive pools across Ethereum, Base, BNB Chain, and Arbitrum.

 Those pools were part of the DeFi Singularity campaign , a 795,000 DOT Polkadot treasury initiative that had actively recruited external LPs into the exact positions that were destroyed.

 Hyperbridge has since identified a third category of losses : Regular users who, during or shortly after the attack, noticed the distorted DOT price in the drained pools and swapped other tokens for a disproportionately large amount of DOT, then bridged it back to Polkadot.

 A 14-day voluntary return window has been opened . Wallets that don't comply will be referred to law enforcement alongside documented on-chain evidence. 

 When the same door gets used more than once before anyone sounds the alarm, at what point does the question stop being about the exploit and start being about who was watching? 

## April Fools Indeed

 Twelve days before the exploit, Hyperbridge announced that the Lazarus Group had drained $37 million across its Ethereum, Arbitrum, and Base deployments. 

 It was a joke. The announcement linked to a now-deleted blog post which contained a Rickroll gif before explaining "Why Hyperbridge Can't Be Hacked". 

 The blog post was deleted. The tweet was deleted .

 The team's real breach announcement opened with "Security Update!", with the replies turned off. 

 Hyperbridge's official statement was careful to draw one distinction: The proof-based model itself , cryptographic proofs generated directly from blockchain state, eliminating the need for validators or multisigs, wasn't what failed .

 What failed was a vulnerability in the Solidity-based MMR proof verification logic, specifically within the Merkle tree verifier implementation . That's a meaningful distinction.

 Founder Seun Lanlege had said as much himself, in a December 2025 interview : "Unless the cryptographic libraries themselves fail, the proofs cannot be forged." 

 That quote didn't survive contact with April 13th. 

 The timing of everything else compounds it.

 Almost a month before the exploit, Polkadot's governance passed a hard supply cap of 2.1 billion DOT with 81% approval - emissions cut by 53.6%, the date set deliberately on Pi Day as a nod to the decay formula.

 Then there is Polkadot's monetary credibility play. The 21Shares TDOT ETF had just launched on Nasdaq on March 6th, offering direct exposure to DOT.

 A governance-enforced supply cap designed to make DOT scarcer. A Nasdaq ETF designed to make it more accessible. Weeks of institutional momentum. 

 Then an attacker forged a proof , took admin control of a bridged token contract, and minted a billion DOT on Ethereum . 

 The supply cap on native Polkadot was never touched. The relay chain was never touched .

 The exploit changed none of that. It didn't need to.

 Hyperbridge's confidence had one audit behind it . That audit had something to say about the Solidity libraries. Nobody followed up. 

 When a deleted blog post turns out to be more accurate than the protocol intended, what exactly does the team owe the people who read it? 

## Read The Report

 SR Labs audited Hyperbridge in June 2024. The report is 26 pages. It is publicly available on GitHub. It has been sitting there for nearly two years. 

 On Page 4 , Table 1, under In-scope components, HandlerV1.sol listed. 

 Priority: High.

 The auditors looked at it. They found issues - one high severity, one medium, three low across the Solidity modules. The high and medium were fixed. Two of the low severity findings were accepted. One low severity finding remained open - a configuration that could be locked due to the finality of updates

 Then, on page 23 , buried in the evolution suggestions section, SR Labs wrote something the Hyperbridge team apparently decided not to act on: 

 "The investigation conducted on EvmHost.sol and HandlerV1.sol was heavily constrained in scope. Based on our investigation we believe that the Solidity implementation requires further analysis from a team specialized in smart contract auditing. We recommend investing further resources into the security of the Solidity codebase, including the associated custom libraries." 

 The associated custom libraries - including the solidity-merkle-trees library that Polytope Labs wrote , the one that contained CalculateRoot .

 SR Labs flagged those libraries , in writing, in the cited audit . Then recommended that a team specializing in Solidity smart contract auditing take a closer look .

 The warning was in the audit. The exploit came later anyway.

 The threat model on page 8 makes it worse. SR Labs explicitly identified "Replay ISMP messages" and "Exploit a bug in validation scheme to accept an invalid transaction" as high-value integrity threats - medium effort, high incentive, high hacking value. 

 The attack that happened on April 13th fits both descriptions precisely. The threat was named. The attack surface was pointed at. 

 This is the audit that Seun Lanlege cited when he told TechCabal in November 2025 that security was Hyperbridge's "core obsession." 

 The same audit where the auditors said the Solidity codebase needed more work and the custom libraries needed specialist review. The same audit where replay attacks against the proof validation scheme were called out as a high-value threat.

 It wasn’t the only warning.

 The January 2025 GitHub security advisory for ismp-grandpa should have been a warning too. A critical vulnerability in the ISMP grandpa crate, a missing negation check that caused the verifier to accept only invalid signatures, was discovered and patched internally. A verifier accepting invalid inputs. 

 Sound familiar? 

 That one was caught before it was exploited. This one wasn't.

 The Hyperbridge exploit didn't stay contained to Hyperbridge.

 On April 14th, the day after the exploit, Polkadot SDK developer sorpaas disclosed a critical vulnerability in the Polkadot relay chain itself : What sorpaas described as a same-class proof verification bug in pallet_mmr, introduced in May 2024, that could have allowed an attacker to submit forged BEEFY offense reports, potentially disabling up to 199 of 600 validators and triggering slashes totaling ~446 million DOT , subject to a 28-day governance window.

 The fix, PR#11738, was merged on April 13th . 

 The bug had been present in the SDK codebase for 702 days and live in production for ~485. 

 The SR Labs audit of Hyperbridge went public in June 2024 , the month after that same bug class was introduced into the Polkadot SDK.

 The auditors were reviewing Hyperbridge's proof verification implementation around the same that bug class entered the Polkadot SDK.

 The disclosure by sorpaas explicitly recommends a full audit of the Polkadot SDK for all proof verification issues similar to Hyperbridge. 

 When an auditor explicitly tells you your custom libraries need more work and you ship anyway, who exactly is surprised when the library fails? 

 The number started at $237,000 and ended at $2.5 million. Neither will make the top of the Rekt Leaderboard. But a protocol that published a joke about being unhackable twelve days before it got hacked earns a story. 

 The door was open and more than one actor walked through it. 

 According to SpecterAnalyst and confirmed by Hyperbridge's own April 16th update , a separate attacker took 245 ETH (~$570,000) before the DOT mint made headlines.

 The main attacker minted a billion tokens and learned, the hard way, that liquidity is a ceiling, walking away with ~$237,000

 On-chain, the two attacks account for approximately $806,000 in confirmed losses.[

 Hyperbridge's revised figure is $2.5 million , citing incentive pool losses across four chains. 

 Hyperbridge says forensics partners have identified the wallets and compiled full transaction histories . A 14-day voluntary return window is open before referral to law enforcement. 

 The April 1st blog post titled "Why Hyperbridge Can't Be Hacked" was deleted. The tweet was deleted.

 What remained was a protocol frozen in place , a bridge that won't reopen until the patch is verified.

 The main attacker didn't wait around. Arkham confirmed the Bridged Polkadot Exploiter sent all funds to Tornado Cash - $269,000 total, with $515 left in the wallet .

 The funds are gone. The questions aren't. 

 One cited audit . One recommendation about the custom libraries. 

 A January 2025 security advisory about a verifier accepting invalid inputs that didn't prompt anyone to check whether the Solidity side had the same problem.

 The cryptographic model wasn't broken. The math was fine.

 What failed was those lines of Solidity that sat between the math and the money - untested at the edges, unreviewed by specialists, and unprotected by a single bounds check that would have cost nothing to write. 

 Hyperbridge's pitch was that bridges fail because humans can't be trusted.

 Turns out libraries need to be read too. 

 When your auditors tell you the custom libraries need specialist review and you publish an April Fools post about being unhackable instead, the joke writes itself, you just have to wait for the punchline. 

 If the cryptographic libraries themselves fail and the proofs can be forged, and you were warned, what exactly were you selling? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

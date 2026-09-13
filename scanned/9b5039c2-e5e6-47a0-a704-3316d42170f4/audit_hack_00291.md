# [H] VerusCoin exploit: $7.54 million left the Verus-Ethereum Bridge on July 23rd , and every signature checked out

## Summary
Severity: High
Target: VerusCoin
Loss: $7,540,000
Published: 7/22/2026
Source: https://rekt.news/veruscoin-rekt
Type: rekt-postmortem

## Details
## VerusCoin - Rekt

 Wednesday, July 29, 2026 VerusCoin - Signature Verification Bypass - Rekt 

 read this article also in : 

 $7.54 million left the Verus-Ethereum Bridge on July 23rd , and every signature checked out. 

 The notary proofs were genuine . The state root was genuine. The Merkle path traced back to a real, validly-signed block. Nothing about the cryptography failed . 

 What failed was the question nobody asked : Did the withdrawal correspond to money that actually existed?

 Two months earlier, the same bridge lost $11.6 million to the same entry path and the same bug class .

 Back in May, the team patched what they found , and cut a bounty deal that returned the bulk of the stolen funds .

 Roughly 2 weeks later, a different attacker walked through a different door into the same room .

 This time there was no negotiation. This time there was no statement. 

 When a bridge proves a withdrawal is authentic but never proves it's funded, is that a bug, or is that the design? 

 Credit: Blockaid , Pyro , Sunsec , QuillAudits , VerusCoin , CertiK , PeckShield , SlowMist , Backward Labs , The Block , DefiLlama 
 Blockaid was first to the wreckage . 

 Blockaid posted : "Blockaid detected a VerusCoin Ethereum Bridge exploit on Ethereum. An attacker used the bridge import path to trigger unbacked Ethereum-side payouts, draining ~$7.54M in ETH, tBTC, USDC, USDT, EURC, MKR, and scrvUSD from bridge reserves."

 Blockaid’s second post drew the line back to May before most people had finished reading the first one: Same bridge contract, same entry path, same bug class. A different attacker and loot wallet.

 PeckShield confirmed the drain and flagged something faster than May's timeline , the exploiter was already feeding funds into Tornado Cash. 

 QuillAudits drew the sharpest distinction of the morning . The attacker hadn't broken a signature or forged a notary key. They'd gotten a fake withdrawal notarized like a real one . 

 Then came the detail that mattered most : checkCCEValues, the function patched after May, had held. This wasn't the old hole reopened. It was a different gap in the same trust boundary.

 SlowMist's post carried the only line-level root cause anyone would publish that day : VerusProof.checkExportAndTransfers verified hashReserveTransfers against attacker-controlled serializedTransfers, along with the source/destination IDs, but never enforced the CCE’s accounting semantics. it failed to parse or validate totalamounts, totalfees, totalburned, or the CTxOut nValue, nor did it verify that the referenced prior CCE outpoint carried sufficient value and assets to cover the claimed transfers. 

 Backward Labs published the only formal incident report anyone would see : The bridge accepted a proven import that authorized multi-asset reserve payouts, violating the invariant that Ethereum bridge reserves may be released only for source-chain reserve transfers whose transfer hash, count, and economic backing are proven under the expected bridge lifecycle.

 Verus said nothing, not the day of the exploit and not a peep since.

 The Block reached out to the team for comment . No word on whether or not they replied. 

 When eight independent security firms can reconstruct your bridge's failure before you've said a word about it, what exactly is the delay buying you? 

## Half a Proof

 To move value from Verus to Ethereum, a user doesn't send a message. They submit a receipt. 

 On Verus, that receipt takes the form of a CrossChainExport output , a commitment to a specific set of transfers, hashed and embedded in the chain. 

 Notaries attest to a state root containing that export . The root is relayed to Ethereum, where the bridge contract verifies the signatures, reconstructs the Merkle path, and confirms the export exists inside a notarized block.

 On Verus, like on Bitcoin, anyone can put any bytes they want in an output script. An export is just a byte pattern, so the contract checks the pattern, not the authority: It checks whether the output parses as an export with the right source and destination, whether keccak256(serializedTransfers) equals the hash field inside it, and whether one of the transaction’s inputs spends the previous export’s transaction hash.

 If those checks pass, checkExportAndTransfers returns successfully , and processTransactions executes the payouts .

 What the contract never asks is the only question that matters: What actually backs the export? 

 Not totalamounts. Not totalfees. Not totalburned. Not the real nValue of the CTxOut being spent. The bridge proves the receipt is real. It never verifies that the receipt is backed by conserved value. 

 On Verus, as with Bitcoin, transaction outputs can carry arbitrary data. An export is just a structured byte pattern, and if an attacker controls both the transfer list and the hash that commits to it, the integrity checks pass by construction.

 The attacker built both sides.

 Vulnerable Contract: 

 0x54e03a1682fd0bb065b669f6296f97028dcfd4ce 

 Bridge Contract: 

 0x71518580f36feceffe0721f06ba4703218cd7f63 

 Step one was trivial : A legitimate 0.01 VRSC transfer through the bridge, just enough to become the most recent export. That satisfies the linkage check of spending from the last export.

 Step two was the forgery : A new Verus transaction spent that output and embedded a hand-crafted export, committing to eight transfers, all payable to the attacker-controlled address. 

 The attacker defined the transfers and the hash that supposedly commits to them. The bridge checked the commitment, not the provenance. 

 Step three required no compromise : Two legitimate notarizations (heights 4162938 and 4162957), each signed by eleven notaries, were relayed to Ethereum as usual.

 The forged export simply existed inside a notarized state root . The bridge proved the export was included in a real block; it did not prove that Verus had actually created it or that it was economically valid.

 Step four was execution : The import submission supplied a valid proof, a valid root, and a matching hash. All checks passed. The bridge paid out.

 May and July are not the same bug at the code level. checkCCEValues, implicated in the first exploit, held this time. The patch addressed a specific failure mode. 

 What it did not change was the assumption one layer above it : That a matching hash implies economic backing. 

 Close one path, and another remains, because the invariant itself was never enforced . The system verifies that a receipt exists, that it is included, and that it is internally consistent. It never verifies that the value it authorizes to leave Ethereum was ever locked on Verus .

 The bridge has now demonstrated, twice, that it can authenticate a receipt.

 It has yet to demonstrate that the receipt is worth anything. 

 If May's fix eliminated the exact path the first attacker used, and a second attacker still reached the same outcome, was that a fix - or just a description of the previous exploit? 

## Eight Transfers, One Transaction

 Whatever the invariant was supposed to enforce, this is what left the moment it didn't. 

 One internal transfer, seven token transfers, all inside a single call - and every one of them sits in public record. 

 Attacker Wallet: 
 0xbda71b58cec0b1c20a8f87ccd52fa0679747855c 

 Loot Wallet: 
 0xcfd0a20703cd11e0b9f665e1c3f1ef989c142d54 

 Exploit Transaction: 0xa1f1e65c1cea4dba4ae439cd4dcdba6cc2dbda0ed1228e61f29ae9c9324eb099 

 Eight transfers, all in one transaction : 1,137.45 ETH, 71.50 tBTC, 149,275 USDC, 92,784 scrvUSD, 78,300 USDT 59.43 MKR, 220,357 DAI, and 31,475 EURC 

 For DAI, the bridge went further, it drew against its MakerDAO position and minted 220,357 DAI to satisfy the withdrawal . 

 Tornado Cash deposits began roughly 90 minutes later.

 Before the mixer, the basket was consolidated. tBTC, the stablecoins, MKR, and the freshly minted DAI were converted and into roughly 3,916 ETH , then laundered through Tornado Cash .

 One token is easier to move than seven, and harder for any single issuer to freeze in isolation.

 The deposits ran in escalating sizes, 0.1 ETH, then 1 ETH, then 10, then a long run of 100 ETH transfers, each one landing in Tornado Cash's router within seconds of the last. 

 By the time anyone thought to check the wallet again, it held about 0.09 ETH . 

 No freeze. No exchange coordination was announced. No recovery address was published.

 In May, the attacker returned 4,052.4 ETH and kept a 25% bounty .

 Whatever calculation made that trade worth it the first time, nothing suggests the July attacker was offered - or considered - the same deal. 

 When laundering takes ninety minutes and negotiation never starts, what exactly is left for a bounty offer to interrupt? 

## Fifteen Days

 In May, Verus had a script for this. 

 VerusCoin redirected people to Discord , with Mike Toutonghi, Verus’s lead developer, giving updates. 

 Bounty terms were posted publicly : The community offered 1,350 ETH as a bounty in exchange for the return of 4,052.4 ETH within 24 hours of the post.

 By May 23rd, the team confirmed 4,052.4 ETH, roughly 75% of the stolen funds, had been returned to community control.

 By May 28th, the recovered funds had been converted back into their original currencies, ready for reintegration.

 On July 8, roughly 1,192 ETH moved from the recovery address back into the bridge contract , part of Verus’s v1.2.17 bridge restoration and recovery update . The rest of the May recovery funds, tBTC and USDC, remained outside that transfer. 

 It went back into the same bridge contract , where the patch had addressed only the specific failure mode identified after May . 

 Fifteen days later, a different attacker found what the patch never touched.

 There has been no Discord post this time. No pinned thread. No bounty offer, no negotiation, no acknowledgment that a second attacker walked through the door the first one used.

 The Block reached out to the team directly. No word on a response, either.

 The silence reads differently the second time. In May, quiet was the pause before a plan. In July, quiet is just quiet. 

 Verus went quiet on social media, but its GitHub release trail continued . The public record shows an urgent bridge restoration release in v1.2.17 on July 3, a follow-up v1.2.17-1 update on July 12 that added an opt-out vote for the ETH bridge contract upgrade , and continued activity across the wallet, mobile, and core repositories. 

 DefiLlama's numbers tell the rest of it without needing a statement . Verus carried roughly $90 million in total value locked at the start of 2025. As of late July 2026, it holds under $5 million.

 A bridge that puts its recovered funds back into an unpatched vault isn't performing recovery. It's performing confidence, and hoping nobody times the gap between the announcement and the next transaction. 

 If the money you get back goes right back into the room with the broken lock, whose recovery was that actually for? 

 The Verus-Ethereum Bridge wasn't beaten by cryptography. It was beaten by an assumption nobody rewrote. 

 Twice now, the contract has proven a receipt is real. Twice now, it has failed to prove the receipt is worth anything. 

 The first time cost $11.6 million and ended in a public negotiation .

 The second cost $7.54 million and ended in silence.

 Sixty-six days sit between them. Fifteen days sit between the partial fund transfer back into the bridge and the second theft . The gap was never hidden. It was just never closed.

 The bridge verified every signature, every state root, every proof it was built to check for, and it still paid out money that had never existed. 

 If the fix that follows this one only patches the function the last attacker used, and leaves the assumption underneath it standing, how many more names does this list need before someone rewrites the invariant instead of the incident? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

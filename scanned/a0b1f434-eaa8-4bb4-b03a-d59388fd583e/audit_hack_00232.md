# [H] SecondFi exploit: Cardano's largest wallet didn't get hacked

## Summary
Severity: High
Target: SecondFi
Loss: $2,400,000
Published: 6/21/2026
Source: https://rekt.news/secondfi-rekt
Type: rekt-postmortem

## Details
## SecondFi - Rekt

 Tuesday, June 30, 2026 SecondFi - Cardano - Rekt 

 read this article also in : 

 Cardano's largest wallet didn't get hacked. It got read. 

 Between June 21 and 23, 2026, external attackers drained roughly 16 million ADA, around $2.4 million, from 374 SecondFi wallets . 

 Then SecondFi moved 129 million ADA to a third-party custodian as an emergency rescue.

 Over the course of the incident response, the platform became both the victim and the mechanism for a second loss of control.

 No contract was exploited, no bridge manipulated, no developer phished.

 SecondFi Android 10.0.3 shipped an Ed25519 signer where the nonce , the per-signature secret that makes private keys irreproducible, was derived entirely from public transaction data. 

 One signature was enough to reconstruct a key . Every spend a user had ever made was a standing disclosure. The chain wasn't attacked. It was read. 

 Taylor Monahan called it worse than 2011-era Bitcoin wallets.

 EMURGO called it a highly sophisticated , pre-meditated, multi-actor exploit enterprise.

 EMURGO, which describes itself as a co-founding entity of Cardano and is the developer of record on the App Store listing , has pledged to return assets of all affected wallet addresses .

 What none of them can do is un-publish the signatures that have been sitting on-chain since before the first wallet was touched. 

 When a single missing line of code makes every transaction your users ever signed a public disclosure of their private key, who owns that window? 

 Credit: SecondFi , Emurgo , hackmd , Charles Guillemet , Tayvano , Cos , 小賤狗 , Cardano Foundation , Tibane Labs 
 The attack window was June 21 to 23 , but the damage started earlier than that. 

 On June 12, a user at address addr1qxvn signed a routine spend of around 1 million ADA. Normal wallet activity, nothing exotic.

 What they didn't know was that SecondFi Android 10.0.3, released four days earlier on June 8 , had shipped with a broken Ed25519 signer, one that derived the per-signature nonce entirely from public transaction data.

 Per the HackMD analysis, any transaction signed through that signer was sufficient for an observer to reconstruct the private key from on-chain data alone.

 June 12 was not when the funds disappeared. It was when the key was exposed. 

 By June 21, automated attackers had started working through exposed addresses. Two independent groups drained 374 wallets across three waves . 

 Attacker A hit 171 addresses in two automated batches.

 Attacker B swept 203 more in a separate automated sweep.

 SlowMist founder Cos, watching the drain unfold over 30 hours , observed that the attacker appeared to have obtained a batch of private keys in advance and worked through them continuously over more than 30 hours, amounts decreasing from large to small.

 SecondFi's first public statement arrived June 22 , describing a security issue affecting a small number of wallets. 

 The platform went into maintenance mode. 

 By the following morning, on June 23 , the team confirmed the root cause was confined to its native Cardano web wallet generation software, and put the preliminary damage estimate at around 16 million ADA .

 A patch for unaffected wallets was confirmed on June 24 .

 Then came the fourth event. Alongside the three external drains, SecondFi confirmed it had moved approximately 129 million ADA to an independent third-party custodian , describing it as emergency rescue measures to protect funds before further attackers could reach them.

 An external accounting firm was engaged to verify the holdings. 

 The custodian's identity was not disclosed. A return framework had not yet been announced. 

 One detail cut through the public framing cleanly.

 Charles Guillemet pulled signatures from mainnet , rebuilt private keys from a single on-chain signature, and confirmed the mechanism held.

 It held across the addresses tested . No device access, no second transaction, no special tooling. Just reading what was already on-chain. 

 That left one question SecondFi never cleanly answered.

 One user reported having originally generated their seed in Daedalus , imported it into Yoroi, and lost funds after the app auto-updated to SecondFi, which raised the question of whether any wallet that signed through the broken signer was exposed, regardless of where the seed came from.

 The HackMD analysis supports that reading . 

 When the vulnerability arrived in an app update, sat undetected for two weeks, and the response to cryptographic exposure was a social promise of custody, how much of what users were told to trust was actually trustworthy? 

## Public In, Public Out

 Every signature scheme in the Ed25519 family uses a per-signature secret number called the nonce. 

 It has one rule : it must be secret and unpredictable. 

 Cardano uses extended Ed25519 , which derives the nonce from the transaction body hash combined with a secret 32-byte suffix called kR , unique per wallet and never published.

 Determinism guards against bad random number generators. The secret kR is what keeps the nonce unguessable to anyone reading the chain . Both properties are mandatory. Drop either one and the scheme breaks.

 SecondFi Android 10.0.3 dropped kR .

 The decompiled Hermes bundle from the shipped APK shows the signing function computing the nonce as SHA-512(M) , where M is the transaction body hash, which is public on-chain. 

 The secret argument, which carries the full 64-byte extended key including kR, is only used later at the challenge computation step, which is too late to affect the nonce . 

 kR is absent from the part of the code where it would need to influence nonce generation , and the consequences follow directly.

 A signature is a pair (R, s), where s = r + k · kL mod L , and k is derived from public values already in the signature.

 With a correctly derived nonce, the equation has two unknowns and cannot be solved from a single observation.

 But if the nonce is a public function of the transaction body hash, then r is computable by anyone, kL falls out immediately, and the key is lost . 

 Classic nonce reuse usually takes two signatures. 

 This flaw needed only one. Every transaction ever signed through the broken signer is therefore a permanent on-chain disclosure.

 The shipped app does not use the public Yoroi and Cardano Serialization Library stack , which correctly hashes kR together with the message. It uses a private implementation instead. Hardware wallet signing uses a separate code path and was not implicated.

 A separate forensic analysis from Tibane Labs , a competing wallet developer, offered a more granular account.

 Tibane argues the broken signer was EMURGO’s in-house SDK , published as @stashers.io/trantor, and that the bug was introduced in the adapter layer that fed the signer key material , not in the underlying cryptographic library. 

 That account differs from earlier descriptions that locate the problem more generally in the bundled signer. 

 EMURGO has not publicly responded to Tibane Lab’s analysis .

 Tibane's findings should be treated as a competing forensic interpretation rather than settled consensus.

 One additional correction came from Taylor Monahan , who pushed back on the framing that only the first or default address at index 0 was at risk.

 Any key that signed a transaction using SecondFi in June 2026 is exposed, regardless of whether it was generated in SecondFi or not. 

 When the only code that could have caught this was proprietary, and the only people who could review it were the same people who shipped it, what exactly was the audit process protecting? 

## First Come, First Drained

 Two attacker groups, operating independently, worked through the exposed address pool across three waves between June 21 and 23 . 

 Attacker A drained 171 wallets across two automated batches , routing funds through three collection wallets and a central fee address. 

 Attacker B swept 203 wallets in a separate coordinated run .

 Total taken by external attackers : Approximately 16 million ADA across 374 addresses, roughly $2.4 million at ADA's price near five-year lows of around $0.146 .

 Attacker A Collection Wallets: 
 addr1q9j7f598x988unr4zhjulft205jqnn9ewgwkhes5smf2sr6jsw98nm4qq38jw9epe587twavuhuhj5d8r92rjvmyjlzs9lqc3x 

 addr1q9wudkfeelzwev427yvapkmqexmet8q4vl303m7a4eerwtvt6rq00zyuqzeuw759vgqtdky0gyxnqx27n8q4k6h79yhsqelma8 

 Addr1q82jlp2u0ezv2hsf6f40fkrv49hd72yv442nmrr5qeultpqamepaykp3m564hnd4zp75wxxds2j6d3ywvc8prhf2kcxqn6nql3 

 Central Fee/Change Address: 
 addr1q8acx4h5a38x6ekpsp0x7aelw6mflt78khmz8lz75rtnqvn07w88zx2e89tgzqr3x0mecngqlg87kq9surhk48hj79mqcezfa8 

 Attacker A Stake Key: 
 Stake1u9hl8rn3r9vnj45pqpcn8auuf5q05rltqzcwpmm2nme0zasf40ymg 

 Attacker B Collection Wallet ( ~4,020,468 ADA remains, flagged and under active monitoring): addr1q8m5wdncq7rwum73r5cyyr82qx2xjem5k4ehapl3wy36aaerj829vasl3amtcwshgvnn6a25dr850tfw6qaj420d2szsslkku6 

 Attacker B Stake Key: 
 stake1uy3er4zkwc0c7a4u8gt5xfeaw42x3n6845hdqwe248k4gpgdq4da5 

 The two figures in public circulation, SecondFi's 16 million ADA and SlowMist Cos’ estimate of over $20 million , measure different things. 

 SecondFi counted only confirmed external attacker drains . 

 SlowMist's Cos tracked broader attacker address flows and estimated that the wallet users had likely lost over $20 million, including more than 129 million ADA and other tokens stolen.

 Separately, SecondFi moved approximately 129 million ADA to an independent third-party custodian , describing it as an emergency rescue measure to protect funds before additional attackers could reach them.

 SecondFi described that sweep as emergency containment , triggered to protect funds before additional attackers could reach them.

 The logic held as far as it went : Keys were publicly recoverable from on-chain data, so more actors with access to the same data could have drained more wallets. 

 Moving funds to custodial storage interrupted that window. 

 What it could not do was resolve the underlying problem. Once a key is recoverable from on-chain data , the original owner and any attacker who observed the signature can derive the same signing authority for that address .

 SecondFi's sweep moved the ADA . It did not restore exclusive control over the compromised keys.

 The secondary risk remained live. Attackers were reported to be monitoring the mempool, so any transaction from a compromised address , including staking reward withdrawals, could be front-run on confirmation . 

 SecondFi's warning was precise : Restoring the same seed phrase into another wallet recreates the same exposed addresses. The vulnerability was in the signing, not the interface. 

 Attacker B's collection wallet, still holding over four million ADA, was flagged and placed under active monitoring .

 As of the June 26 recovery update , those funds had not moved. 

 When a key compromise means the original holder and any attacker who read the chain hold the same signing authority over an address, what does recovery actually mean? 

## Custody Theater

 SecondFi moved into containment, but containment is not the same as control. 

 Users were told not to restore seed phrases into another wallet, not to withdraw staking rewards, and not to move funds independently , because any action from a compromised address could expose the same keys again. 

 The warning was correct. It was also the only thing left to say after the platform had lost the ability to protect its users cryptographically.

 The 129 million ADA sweep may have stopped additional drains . What it could not do was restore control.

 Once signatures on-chain can be used to reconstruct private keys, custody is not a fix so much as a holding pattern. The platform could move the assets. It could not un-publish the signatures that made them vulnerable in the first place.

 That is the sharpest edge of this incident. The chain did exactly what it was told to do. 

 What it was told to do was unsafe. A broken signer turned ordinary wallet activity into key disclosure , and once that happened, the question of who held the ADA became a matter of social trust rather than cryptographic fact. 

 EMURGO has pledged to return funds . A restoration fund has been established.

 An external accounting firm is verifying the custodian holdings.

 All of that is paperwork built on top of a problem the paperwork cannot solve. 

 By June 29, the shape of that paperwork had become clearer. SecondFi confirmed that EMURGO had funded a dedicated Asset Recovery Wallet to return funds to wallets drained by external attackers . 

 For the 129 million ADA swept in the emergency containment, SecondFi said it was in active discussion with IntersectMBO on the appropriate custody mechanism to hold those funds securely before returning them to users .

 The custodian's identity had still not been disclosed.

 A week into the incident, that question remained open. 

 If the fix for a cryptographic failure is a pledge and an accounting firm, who is actually being protected? 

 Two months before SecondFi's drain window , Volo faced a structurally similar situation on Sui. 

 A private key was compromised, no code was broken, and $3.5 million left three vaults before any security researcher had flagged anything . 

 Volo disclosed it themselves , within hours, coordinated with ecosystem partners, intercepted the WBTC bridge attempt, and recovered $3.44 million within days .

 The net loss absorbed from treasury was $60,000. Zero passed to users.

 In both cases, the security failure came down to key compromise rather than a broken contract.

 The response diverged sharply: Volo acted fast and recovered most of the funds, while SecondFi was still working through remediation. 

 SecondFi's recovery timeline, announced June 26 , estimated funds could begin being returned roughly two weeks out. 

 By June 29, that estimate had already shifted. SecondFi confirmed the on-chain recovery solution was more complex than originally anticipated and may require additional time beyond the two-week window.

 A mechanism for users to check whether their wallet was affected was promised by early the following week.

 The custodian has not been publicly named .

 No public commit history has been released that would clarify how the broken nonce came to be . 

 If a single missing secret input can turn every signature into a public key disclosure, what exactly are users supposed to trust the next time a wallet says self-custody? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

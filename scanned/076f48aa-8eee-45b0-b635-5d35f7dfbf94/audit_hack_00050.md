# [H] Bonzo Finance exploit: On July 11th, an attacker dropped 250 SAUCE tokens , worth about $3 , into Bonzo Lend, wrote themselves a price twelve orders of magnitude too high ,

## Summary
Severity: High
Target: Bonzo Finance
Loss: $9,050,000
Published: 7/11/2026
Source: https://rekt.news/bonzo-finance-rekt
Type: rekt-postmortem

## Details
## Bonzo Finance - Rekt

 Tuesday, July 14, 2026 Bonzo Finance - Signature Verification Bypass - Rekt 

 read this article also in : 

 Zero equals zero. That was the entire cryptographic proof standing between Hedera's largest lending market and a $9.05 million bleed-out . 

 Not a forged signature. Not a stolen key. An absence, mistaken for a presence. 

 On July 11th, an attacker dropped 250 SAUCE tokens , worth about $3 , into Bonzo Lend, wrote themselves a price twelve orders of magnitude too high , and waited eight seconds.

 Eight seconds bought 6.63 million USDC and 34.5 million WHBAR against what was functionally dust.

 No flash loan . No reentrancy. No key ever cracked, because no key was ever checked . 

 Supra's verifier accepted the malformed update , and the pairing check returned true.

 Bonzo's contracts read the number they were handed and did exactly what they were built to do.

 The precompile answered the question correctly . The verifier failed to validate the inputs first. 

 When the equation checks out and the money is still gone, who exactly authorized the withdrawal? 

 Credit: Pyro , Bonzo Finance , Supra , CoinGecko , Specter , Hedera , Cos , QuillAudits , Joshua Tobkin , Peckshield 
 00:39 UTC, July 11th, wallet A deposits 250 SAUCE into Bonzo Lend . Nobody notices, why would they, it was worth roughly more than $3 . 

 Twelve minutes later, the same wallet submits a price update to Supra's on-chain oracle .

 SAUCE, trading at roughly a penny and a half, suddenly prices out at twelve orders of magnitude higher .

 Eight seconds after that, 6.63 million USDC and 34.5 million WHBAR leave the pool .

 Bonzo's own channels catch up first with the vaguest possible language , "investigating volatile markets," a pause, a link to a status page . No dollar figure. No mention of an exploit. 

 Onchain Investigator Specter got there first with the initial details : There appears to be an ongoing hack involving Hedera Network, with over $3.7 million already bridged to Ethereum through LayerZero, stolen funds swapping from WBTC into ETH. 

 The number kept climbing across separate posts, past $4 million , then past $5 million , then confirmation the proceeds are heading into Tornado Cash .

 Bonzo then published the official accounting : The incident would ultimately be pegged at $9.05 million in principal extracted by the attacker, with roughly $1 million more tied to the white-hat responder

 Hedera's own account draws a line nobody else had drawn yet, this isn't a chain-level failure : "Hedera's consensus mechanism and core network services were not compromised, and mainnet remained operational."

 The blame lands on a third-party oracle verifier, and Hedera named Supra directly , in public, a day before Supra says a word itself . 

 By 09:49 UTC , Bonzo publishes its full incident report , the document that would eventually account for every wallet, every timestamp, every zeroed signature. 

 Cos, founder of SlowMist, reduces the mechanism to one sentence anyone can parse : The attacker's signature and public key were both zero, so "both sides of the underlying mathematical verification equation simultaneously became 0," and the check passed anyway.

 QuillAudits closed the attack loop with addresses, transaction hashes , and then a route, Arbitrum, Base, Ethereum, then Tornado Cash .

 Same mixing playbook every exploit reaches for eventually, just with a fresher disguise this time. 

 When the people tracing the stolen money move faster than the protocol that lost it, who's actually running the incident response? 

## Two Years Naked

 The mechanism itself sounds almost too simple to justify a nine million dollar exploit. 

 Supra's pull oracle lets anyone submit a price update , provided the accompanying proof passes a BLS signature check run through Hedera's pairing precompile. 

 The attacker referenced a committee ID that sat outside the range Supra had populated.

 Instead of rejecting that reference , the lookup quietly returned a public key of all zeros. Pair a zero signature with a zero key and the equation holds automatically, because both are the BLS identity element.

 The precompile did its job and answered correctly. The verifier's job was to reject exactly that kind of degenerate input before it ever reached the precompile, and it never did.

 Supra's own postmortem is candid about the fix , three separate checks now stand where zero once stood, range validation on the committee lookup, rejection of identity element keys and signatures, and on curve validation before anything reaches the pairing check. 

 Supra states it plainly : "The identity-element check alone would have prevented this attack." 

 What makes this story different is what came after the technical writeup.

 Joshua Tobkin, Supra's co-founder and CEO, posted directly to the hacker, or hackers, responsible , and buried inside that negotiation sits the detail that reframes the entire incident.

 The flawed verifier had been live , unpatched, fully on-chain and visible to anyone, for two years. 

 " Live. Transparent. For two years straight ," he wrote, through an entire bull market, before landing on the line that will get quoted for a while, " Anyone could have found it. Nobody did. Not until now ." 

 His theory for why now , after two years of silence, is AI.

 Tobkin frames it as a new class of adversary , one that "reads every line, every branch, every edge case," a tireless auditor human reviewers never had to compete with before.

 Whether or not this specific exploit came from an AI assisted search, the claim itself says something uncomfortable out loud, every protocol audited by a human team was audited against a threat model that may no longer exists. 

 A blind spot sat in plain sight for two years. Where did the nine million dollars it eventually produced actually end up? 

## Naked Negotiation

 Money doesn't sit still after an exploit like this, it runs. 

 And run it did: within minutes, a chunk of the loot was already crossing chains off Hedera via LayerZero , with Stargate as the bridge QuillAudits named, hitting Arbitrum, Base, and Ethereum along the way . 

 By the time it settled, the receiving wallet held roughly $5.25 million, close to 2,360 ETH and 15.58 WBTC , WBTC and stablecoins swapped down into ETH as it moved, before most people had finished their coffee.

 Peckshield highlighted that the same wallet had been seeded ten hours earlier with a single ETH sent from Tornado Cash , the kind of detail that tells you this wasn't anyone's first attempt at this.

 Here’s the trail it left behind, from the forged attestation to the wallets and contracts that carried the rest of the story.

 The forged attestation itself - Committee ID referenced in the fraudulent submission : 2

 Different from a transaction hash, this is the message root the forged signature was supposed to correspond to.

 Committee hash, the message root the forged signature was supposed to correspond to : 0xd4e6b48aef731cc8cd74b25fbaec267ff8a6269aea1f4be4ee19dda5ecbf3f7f

 Oracle pair targeted : 425, SAUCE / wHBAR

 Transaction hashes are as follows… 

 The first is the Hedera transaction ID; the second is the EVM-compatible hash for the same Hedera transaction. 

 Manipulated price update: 

 Hedera Transaction ID: 

 0.0.995584-1783731093-686041919 

 EVM-compatible Hash : 

 0xd50c55e24eb8483ec55bf74e84fc9853d0f0fe36f64abdb812a2d9afa2a10a60

 SAUCE collateral deposit: 
 1783730393.018023002 

 USDC drain: 
 1783731107.330069002 

 WHBAR drain: 
 1783731117.865661002 

 Wallets and accounts are as follows… 

 Wallet A, primary attacker’s Hedera Account: 

 0.0.10633526 

 Wallet A, primary attacker’s EVM Alias: 

 0x9a4966152f6e10b33cb7a37975e8619816d6a494 

 Wallet A, linked EVM address used once funds bridged over to Ethereum: 0xaf20D792A19fD42dCf697ceBa6100291D96dD93e 

 Wallet B, the self identified white hat responder, Hedera account: 

 0.0.683607 

 Contracts are as follows… 

 Supra pull oracle: 

 0.0.4323024 

 Supra verifier, requireHashVerified_V2, where the flaw actually lived: 

 0.0.4323006 

 Hedera pairing precompile, system contract : 0.0.8

 Bonzo LendingPool proxy: 

 0.0.7308459 

 Bonzo SupraOracle adapter (Bonzo-owned integration code): 

 0.0.7308480 

 Every one of those identifiers is public. Anyone can pull them up on HashScan or Etherscan

 right now, and still, as of this writing, nobody has put a name to the wallet holding the money.

 That's the backdrop Joshua Tobkin negotiated against , in public, on Twitter, addressed directly to the person or people who did this.

 The terms were blunt. Keep $100,000, return the rest, walk away with no charges and a guaranteed job offer. Refuse, and the bounty on your head grows ten percent a year, forever, payable to whoever eventually turns you in. 

 Seventy two hours , one wallet, built specifically to receive it. 

 Supra's return address: 

 0x913BDd807608DEA920C689a7c3222E94e07551cC 

 Whether that address ever receives a cent is a separate question from whether it should exist at all.

 A standing bounty is not the same thing as a recovered dollar, and right now Bonzo's principal, Wallet B's promised return included , is still just a number on a spreadsheet somewhere.

 A nine million dollar loss sounds like a story with a bounty on it, until you remember no one has actually recovered the money. 

 Was that offer built to recover funds, or to buy time? 

## Wrong Contract Audited

 Bonzo did what a lending protocol is supposed to do. 

 Halborn's name sits against its lending contracts , its liquidity incentives, its staking module, its LayerZero bridge connector, and its vaults, and none of those reports point to Bonzo's own code as the cause. 

 The protocol's own documentation leans on that same diligence too, with Chainlink and Supra as the two named providers, though SAUCE and wHBAR relied on Supra alone .

 Chainlink's integration covers HBAR and USDC , nothing tied to the pair that was hit. Redundancy works exactly until the asset that gets hit turns out to be the one nobody doubled up on.

 Bonzo does have a scope document, and it turns out to be more damning than having none at all.

 The company's own bug bounty program lists exactly what's covered , its lending contracts, its vaults, its staking module, and just as precisely, what isn't, " Out of scope: third-party contracts not directly associated with Bonzo Finance ." 

 Supra's verifier is exactly that, a contract Bonzo depends on and reads from but never owned, so by Bonzo's own written policy, nobody would be paid for finding a bug in it . 

 Supra's own paper trail is stranger still, because there's no audit scope for the contract that failed, not even one that carves it out.

 The one named audit of Supra's oracle work on record is a MoveBit report from years before the exploit , scoped to Supra's Aptos contracts, written in Move, running on an entirely different chain.

 The Hedera pairing check that actually failed , requireHashVerified_V2, never shows up in it , because it was never in scope. Not carved out. Never there in the first place.

 Tobkin said the bug sat live and visible for two years , missed by every reviewer in the world. 

 That claim gets a lot easier to believe once you notice there's no record of any reviewer, anywhere, ever actually looking at that piece of code. 

 His own metaphor explains the section title better than anything we could add on top.

 Being a founder in DeFi , he wrote, feels like the nightmare of “showing up to school naked,” and this exploit made it literal: “we’re all naked in the hallway now.”

 Buried further down , almost in passing, is the line that belongs here most of all: Supra had “recently started” formal verification work, which he called “ironic,” given what had just happened.

 Bonzo wrote a policy that excluded this dependency on purpose. Supra, by its own CEO’s account, had not yet formally verified it. 

 Being out of scope on paper is one failure. Never having a scope document for the contract that mattered is a different one entirely, which is worse? 

 Zero equals zero, and that one equation will outlast every headline this exploit generated. 

 Nine million dollars was extracted because a verifier trusted a correct answer to the wrong question . 

 Three checks would have stopped it , all added too late. Instead the flaw sat exposed for two years, missed by human reviewers, and it took something faster than a human, by the Supra CEO's own account, to finally find it .

 The stolen funds crossed three chains and a mixer before anyone could put a name to a wallet, and a bounty now stands in place of an actual recovery .

 Bonzo's contracts passed every audit thrown at them , and none of that mattered, because the number they were handed was a lie, not the logic that processed it.

 Every protocol still running on someone else's verifier is quietly betting its own two year old blind spot hasn't been found yet either. 

 If checking for zero was the entire fix, what else out there is everyone still assuming was never zero? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

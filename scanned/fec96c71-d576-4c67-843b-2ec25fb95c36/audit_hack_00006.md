# [C] Abracadabra - Rekt II exploit: Abracadabra Money just performed its most impressive vanishing act yet - $13 million in ETH disappeared in the blink of an eye

## Summary
Severity: Critical
Target: Abracadabra - Rekt II
Loss: $12,913,691
Published: 3/25/2025
Source: https://rekt.news/abracadabra-rekt2
Type: rekt-postmortem

## Details
## Abracadabra - Rekt II

 Wednesday, March 26, 2025 Abracadabra - Rekt 

 read this article also in : 

 Abracadabra Money just performed its most impressive vanishing act yet - $13 million in ETH disappeared in the blink of an eye. 

 The lending platform's GMX-linked pools were drained of 6,260 ETH after attackers discovered a liquidation loophole hiding in plain sight. 

 While GMX rushed to distance itself , insisting “no issues have been identified with GMX contracts,” Abracadabra was left staring at empty cauldrons and a $13M-shaped hole in its books.

 This marks Abracadabra’s second major exploit, following their January 2024 $6.5M precision loss exploit - another blow to Magic Internet Money , which is looking less like a stablecoin and more like a disappearing act.

 The attackers crafted a masterpiece of financial sleight-of-hand, transforming failed deposits and liquidation bugs into a personal money printer that would make even central bankers jealous. 

 Is Abracadabra secretly more talented at making millions vanish than any Vegas magician could ever dream to be? 

 Credit: Vladimir S , Peckshield , Abracadabra , GMX , DCF God 
 Eerily foreshadowed by DCF God , who hours earlier spun a cautionary tale about founders rewriting reality when debts go bad. 

 At the time, it was just another Crypto Twitter theory - until $13M vanished, and Abracadabra was left scrambling for answers.

 Vladimir S, aka Officer’s Notes , was the first to sound the alarm, tagging PeckShield, who quickly confirmed the worst - Abracadabra’s GMX-linked cauldrons were being drained in real-time.

 The stolen 6,260 ETH didn't stick around for long.

 Like clockwork, the funds were bridged from Arbitrum to Ethereum and dispersed across three separate wallets. 

 While the funds were frantically being shuffled around, the usual DeFi blame game began. 

 GMX immediately went into damage control mode, insisting their core contracts remained unscathed - the equivalent of saying "we just supply the kitchen, not our fault if someone burns down the restaurant."

 Abracadabra acknowledged the exploit , insisting their gmCauldrons had been "fully audited by Guardian Audits ."

 They also name-dropped zeroShadow along with Chainalysis for tracking and Hexagate response software - fancy tools, but not much help when $13M disappears without resistance. 

 So how did Abracadabra's magic show go so horribly wrong? 

## The Anatomy of a $13M Magic Trick

 Rekt News reached out to Guardian Audits for details on the exploit. 

 The verdict? This wasn’t some high-level cryptographic sleight-of-hand. It was like finding the stage door wide open, with the cash box sitting in plain sight. 

 The slight of hand was brutally efficient though:

 The Setup: Deposit into GMX, but make it fail. The tokens don’t return to the attacker. Instead, they get stuck in the OrderAgent contract, waiting to be claimed.

 The Misdirection: Borrow funds and push the position into liquidation. Everyone focuses on the liquidation, but the real trick is already in motion.

 The Switch: Self-liquidate. The contract wipes the position but forgets to scrub the order. The collateral? Still hanging around like an unpaid bar tab.

 The Reveal: Borrow against a ghost. The system, blissfully unaware, still sees the liquidated position as good collateral. 6,260 ETH exits stage left—while everyone’s eyes are on the wrong trick.

 No advanced math needed - just a protocol that couldn't keep track of what it had already liquidated.

 Abracadabra promised magic. Instead, they pulled a vanishing act - on their own money.

 The money may have ghosted the cauldron on Arbitrum, but it resurfaced on Ethereum - ready to continue its haunt. 

 Let’s track the phantom’s footsteps… 

 Attacker Address: 
 0xAF9e33Aa03CAaa613c3Ba4221f7EA3eE2AC38649 

 Exploited Cauldron Address: 
 0x625Fe79547828b1B54467E5Ed822a9A8a074bD61 

 Attack Transaction: 
 0xed17089aa6c57b7d5461209e853bdb56bc3460a91805e20d2590609a515ef0b0 

 The stolen funds (6,260 ETH in total) were bridged from Arbitrum to Ethereum and are currently held in the following 3 addresses: 

 0xa8f822E937C982e65b0437Ac81792a3AdA76A1ff 

 0x047C2a3dd1Ab4105B365685d4804fE5c440B5729 

 0x018182FD7B856AeE1606D7E0AA8bca10F1Cb0b5d 

 Abracadabra paused all borrowing and trotted out a 20% bounty offer , but the attacker had already split town with their 6,260 ETH.

 So who cleans up the mess when the money’s gone and the exploit’s already written into DeFi history? 

## The Clean Up

 Guardian Audits skipped the usual blame-shifting dance and owned their miss when Rekt News came knocking. 

 The exploit waltzed through their review while they were busy catching other bugs in the same codebase - they spotted multiple issues but completely missed how a failed deposit and self-liquidation could create a phantom collateral position that remained borrowable. 

 Their response? Double the security squad and slap on invariant testing - a rare sign that at least one audit shop cares more about actual security than collecting protocol badges.

 Abracadabra rushed out their " Path Forward " document the day after the exploit, promising to buy back 6.5 million MIM and cover half the damage upfront.

 They've vaguely promised to absorb the remaining debt "over the coming months" - the crypto equivalent of "the check's in the mail."

 They claim that their treasury still packs enough punch to expand into Berachain, Nibiru, and HyperEVM. 

 Nothing screams battle-tested protocol quite like rushing to deploy your twice-hacked codebase across even more chains. 

 Meanwhile, they're playing detective with Chainalysis, chatting up exchanges, and leaving the door open for the hacker to negotiate a bounty.

 The stolen funds still sit comfortably across those three wallets, undisturbed by law enforcement or bounty hunters.

 Each passing day makes recovery less likely while Abracadabra's grand plans for expansion continue unabated. 

 When DeFi protocols keep treating eight-figure hacks as just another Tuesday, why do we still pretend security matters more than shiny new features? 

 Magic requires misdirection, and Abracadabra's $13M disappearing act has redirected attention from their previous $6.5M January 2024 failure - a neat trick that only works in crypto's goldfish-memory ecosystem. 

 GMX pulled off a flawless reputation rescue, doing the " keep my name out your mouth " dance while letting Abracadabra burn. 

 Despite back-to-back multi-million dollar hacks, Abracadabra insists this is merely a "moment of reinforcement" rather than collapse.

 Their solution? More integrations, more chains, more complexity - because when your house is on fire, the best response is clearly to build an addition.

 Abracadabra DAO’s treasury might buy them another chance. But almost half of their holdings are in MIM and SPELL .

 But no amount of MIM and SPELL can hide the fact that twice-hacked protocols rarely stick the landing on their third performance.

 Meanwhile, as exploits pile up like bodies in a horror movie sequel, DeFi's appetite for self-destruction continues unabated - Frog Nation's remains still drawing flies long after Daniele Sesta's empire crumbled. 

 When your biggest magic trick is convincing users to deposit funds after you've already lost almost $20M to smart contract exploits, who's really getting played here? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

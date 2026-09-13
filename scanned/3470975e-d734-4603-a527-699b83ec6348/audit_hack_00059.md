# [C] Cetus exploit: Cetus Protocol learned the hardest lesson in DeFi mathematics when attackers exploited a flaw in their get_liquidity_from_a formula, turning microscop

## Summary
Severity: Critical
Target: Cetus
Loss: $223,000,000
Published: 5/22/2025
Source: https://rekt.news/cetus-rekt
Type: rekt-postmortem

## Details
## Cetus - Rekt

 Friday, May 23, 2025 Cetus - Rekt - Sui Network 

 read this article also in : 

 One SCA token. That's all it took to mint 10^34 units of liquidity and drain $223 million from Sui's largest DEX on May 22nd. 

 Cetus Protocol learned the hardest lesson in DeFi mathematics when attackers exploited a flaw in their get_liquidity_from_a formula, turning microscopic tick ranges into astronomical liquidity positions. 

 Price intervals 200 ticks apart became weapons of mass destruction - the attackers minted massive positions with pocket change, then cashed them out for genuine SUI and USDC while leaving nothing but mathematical chaos behind.

 Every single Cetus AMM pool got hit. While Sui validators frantically froze $162 million mid-heist , over $60 million had already crossed the Wormhole bridge to Ethereum and transformed into almost 21,000 ETH.

 The attackers knew their math homework - sometimes the tiniest denominators create the biggest explosions.

 They didn’t need zero-days. No oracle tampering. No blockchain wizardry. Just weaponized arithmetic and a protocol that couldn’t divide by almost-zero without losing its mind. 

 When your protocol's greatest strength becomes its fatal weakness, who's watching the watchers watching the math? 

 Credit: HODLFM , Anbessa , SUI Network , Cetus , Verichains , Quill Audits , Chaofan Shou , Leader Alpha , Dedaub , Kriya , FlowX , Turbos 
 Sui’s DeFi dream turned into a liquidity nightmare - overnight. 

 What started like any other Thursday morning ended in what looked like a full ecosystem collapse.

 HODLFM sounded the alarm in the early hours on Thursday.

 “USDC on Sui depegged to zero. Someone has removed the liquidity, all the $SUI tokens are dumping.”

 A few minutes later, the bloodbath was undeniable. 

 Liquidity pools drained like bathtubs. Token prices cratered roughly 80% in minutes while Bitcoin was printing new all-time highs.

 BULLA. HIPPO. LOFI. The meme coins died first.

 Sui Network acknowledged the disaster with corporate speak: "We became aware of an incident concerning Cetus." 

 Cetus followed with their own understatement: "There was an incident detected on our protocol."

 Incident. That's one way to describe $223 million evaporating through a math error.

 Someone had ripped the math out from under the entire protocol - and they knew exactly what they were doing. 

 So how do you turn pocket change into generational wealth — and repeat it until the protocol is bled dry? 

## How to Turn One Token Into $223 Million

 Thanks to a technical breakdown by the team at Verichains , we now know just how simple - and stupidly powerful - the exploit was. 

 It didn’t take sophisticated exploits or advanced cryptography. Just a clever abuser and a protocol that didn’t sanity-check its own equations. 

 (A Step-by-Step Guide to Breaking DeFi)

 Step 1: Take out a flash loan. 

 The attacker borrowed 56,700 SUI - money that had to be returned within the same transaction or the whole thing would revert. Risky? Not if your math is sound. Or broken. 

 Step 2: Pick your price range. 

 They created a liquidity position between ticks 300,000 and 300,200 - just 200 ticks apart. A narrow band, seemingly harmless. 

 Step 3: Add the tiniest deposit possible. 

 They dropped in 1 SCA token. Just one. 

 Step 4: Let the math implode. 

 This is where Cetus’ concentrated liquidity math went off the rails. 

 The get_liquidity_from_a function was supposed to calculate how much liquidity you get for a deposit. But when the tick range is that tight, the denominator approaches zero.

 And what happens when you divide by almost-zero? You get infinity.

 According to analysis by Dedaub , the protocol even had overflow checks - but they didn't cover this particular path. The attacker threaded the needle perfectly.

 That 1 SCA token ballooned into: 
10,365,647,984,364,446,732,462,244,378,333,008 units of liquidity.

 That’s 10³⁴ - a number so large it needs its own postal service. 

 Step 5: Cash out - twice. 

 First withdrawal: just enough tokens to repay the flash loan. 

 Second withdrawal: pure profit.

 Cetus’ accounting was so broken, the protocol let the attacker withdraw the same LP position twice - once to repay the loan, once for profit.

 Rinse. Repeat. Across every pool.

 The attacker didn’t need a zero-day. Just a zero denominator.

 They turned arithmetic into a money printer - and nobody was watching the math. 

 But once you've stolen $223 million... where do you take it? 

## Following the Breadcrumbs

 Every blockchain heist leaves breadcrumbs. The trick is following them before they disappear. 

 Attacker's Sui Address: 
 0xe28b50cef1d633ea43d3296a3f6b67ff0312a5f1a99f0af753c85b8b5de8ff06 

 Attacker's Ethereum Address: 
 0x89012a55cd6b88e407c9d4ae9b3425f55924919b 

 First rule of crypto crime: convert your stolen meme coins into something liquid. 

 The attacker began systematically swapping drained LP tokens into USDC - the preferred fuel for fast exits. 

 When you need to move funs fast, stablecoins don’t ask questions.

 Over $60 million was bridged to Ethereum via Wormhole.

 Never keep stolen funds in the crime wallet. The fresh address was prepped and waiting. 

 20,000 ETH moved to a clean wallet: 
 0x0251536BfcF144B88e1aFa8fe60184Ffdb4cAF16 

 The 20k ETH was sent in a batch transfer: 

 0x787a0bc6305f26c9c6b78155f3271d4f3b8c321245881ee068a84dba04c8c2c0 

 Final Tally: 

 Total initially stolen: $223 million

 Sui validators froze: $162 million

 Still in the Wild: $60+ million

 The attacker had done their homework. 

 But when the math is flawless and the money’s gone, what comes next - justice or just another protocol post-mortem? 

## The Domino Effect

 Here's where Sui showed something most blockchains can't: the ability to hit the brakes mid-heist. 

 But here's the thing about emergency brakes - someone has to pull them. 

 Sui's validators didn't just freeze accounts through normal consensus. They leveraged built-in code mechanisms to execute emergency votes where validators agreed to collectively freeze the funds.

 No signed transaction needed . No smart contract logic. Just validators collectively agreeing to quarantine the hacker's balance from the network.

 $162 million frozen when validators decided to treat the attacker's address as radioactive - emergency consensus overriding normal protocol rules.

 Fast? Absolutely. Effective? Undeniably. Decentralized? That's where things get interesting. 

 When your ecosystem's largest liquidity provider gets drained, everyone else runs for the exits. 

 Other Sui DEXs didn't wait around to become collateral damage: 

 Bluefin : "We've temporarily paused actions on Bluefin Spot as a precautionary measure."

 Momentum : "Due to the ongoing exploit on Cetus, we temporarily paused all activities on Momentum as a precautionary measure"

 The ripple effects of the exploit extended beyond Cetus , prompting swift action across the Sui ecosystem. 

 Many of the tokens on SUI suffered dumped at least 75% shortly after. 

 But what about those audits everyone trusts?

 Just on April 24th, Cetus bragged they had undergone multiple audit rounds by three different top-tier audit firms.

 Movebit and Otter audited Cetus 2 years ago .

 The latest audit done by Zellic was completed on April 11th.

 Zellic's co-founder mentioned : "We're unable to share more details right now as it's an evolving situation, but the bug was out of scope for our audit."

 Zellic later clarified to Rekt: "The vulnerability was not part of the scope Zellic audited. For public details that we're at liberty to disclose, the vulnerability was part of the integer-mate library in the checked_shlw method. But the integer-mate library was not included in the scope of our audit."

 The inter-mate library. The mathematical foundation everything was built on. The vulnerability that drained $223 million wasn't even in the audit scope completed just 41 days earlier. 

 So what happens when your audit misses the part that breaks your entire protocol? 

## The Art of the Deal

 Faced with a $223 million breach and $60 million still unaccounted for, Cetus and Inca Digital issued a message to the attacker . 

 Not through lawyers. Not through backchannels. But directly, on-chain - in broad daylight. 

 Return the funds. Keep $6 million. Walk away. No consequences.

 Signed by Inca Digital and Cetus , they formally offered the attacker a whitehat settlement, the attacker could keep 2,324 ETH (~$6M) as a “bounty,” and Cetus would consider the matter closed - no legal action, no tracking, no public chase. 

 The offer was time-sensitive. If funds were off-ramped or mixed, full global escalation would follow.

 This wasn’t just a bounty offer - it was an ultimatum.

 When $6 million is the price of forgiveness… 

 Is it about stopping attackers anymore, or just making sure they send an invoice first?

 By Friday, the hacker's silence was deafening. No response. No negotiation.

 So Cetus and Sui Foundation pulled out the big guns : 

 "UPDATE: We have not received any communication from the hacker. We encourage the hacker to sincerely consider our offer terms." 

 Translation: Please, pretty please?

 But then came the escalation from Cetus : 

 "Simultaneously, with the support of Inca Digital and financial support from Sui Foundation, we are announcing a bounty of $5M for relevant information that results in the successful identification and arrest of the hacker(s)." 

 From $6 million "please sir" to $5 million "wanted dead or alive" - the negotiation playbook when you realize the other side has already left the building with your money.

 The desperation was palpable. Because nothing says "we've got this under control" like turning your incident response into a crowdsourced manhunt. 

 But while Cetus was busy printing wanted posters, was there a darker truth was emerging from the wreckage? 

## The Copy-Paste Catastrophe

 What started as "Cetus got rekt" was about to become "holy shit, others on Sui were running on the same broken math." 

 Verichains dropped a bombshell report using their Revela Move Decompiler that revealed the truly terrifying scope: Cetus wasn't alone in their mathematical madness. 

 The shared checked_shlw(u256) function - a mathematical landmine copy-pasted across the ecosystem:...

 Kriya : $10M TVL, same bug, quietly patched after the Cetus meltdown.

 Flow X : $4.6M TVL, same bug, silently fixed in the aftermath.

 Turbo Finance : $10.3M TVL, vulnerable code present but unused - a loaded gun with the safety off.

 As Verichains grimly noted : "dead code is not safe code." 

 To their credit, Kriya and Flow X rapidly addressed the situation and apparently deployed fixes once alerted . 

 Turbo? They claim their “smart contracts are independent of Cetus and the exploit method would not have been possible on Turbos.”

 Suddenly that "out of scope" audit excuse takes on new meaning.

 How many protocols audited everything except the shared math library everyone was using? 

 It's like checking every window in the house while leaving the front door wide open because "that's the door vendor's responsibility." 

 Verichains found three. Are there others in the wild?

 Verichains and the Sui Network team deserve credit for one thing: they moved fast to identify and alert other protocols once the pattern was discovered.

 But that's like praising the fire department for arriving quickly to a fire that building codes should have prevented.

 Three protocols. Same vulnerability. $24.6 million in combined TVL sitting on the same ticking time bomb. And these are just the ones we know about. 

 Everybody else getting their code checked? 

 One token. One formula. One denominator approaching zero. $223 million gone. 

 Cetus Protocol didn't just lose $223 million to bad math - they revealed that multiple Sui protocols were running on the same broken mathematical foundations. 

 They built their sophisticated DEX, got their premium audits, secured their institutional backing, then watched a single SCA token turn their entire protocol into confetti.

 The attackers didn't just hack Cetus - they just did the math homework that nobody else bothered to check.

 While Sui validators hit the emergency brakes and froze most of the loot, $60 million still walked out the door with the composure of someone who knew exactly what they were doing.

 Decentralization? That died the moment validators collectively decided to quarantine an address. Turns out "code is law" has an asterisk: unless we really need that money back. 

 Here's the kicker: when your auditors shrug and say "out of scope" after a quarter-billion-dollar meltdown, and your Plan B involves publicly begging hackers to accept a $6 million tip, then escalating to a $5 million bounty when they ghost you, you're not running a protocol - you're running a very expensive math tutoring service. 

 When multiple protocols share the same broken mathematical foundations, you don't have isolated incidents - you have systemic risk with a large price tag.

 The real audit wasn't done by Zellic or Movebit or Otter - it was done by an anonymous mathematician who invoiced for $60 million.

 The three-act tragedy of Cetus... 

 Act 1: "We got exploited for $223 million"

 Act 2: "We'll pay you to give it back"

 Act 3: "Oh god, who else has the same bug?"

 When your security depends on hoping nobody checks the math - is it security or just prayer? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

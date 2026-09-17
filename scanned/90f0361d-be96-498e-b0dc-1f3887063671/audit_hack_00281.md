# [H] USPD exploit: A hacker living rent-free in your admin slot for nearly three months?

## Summary
Severity: High
Target: USPD
Loss: $1,000,000
Published: 12/4/2025
Source: https://rekt.news/uspd-rekt
Type: rekt-postmortem

## Details
## USPD - Rekt

 Monday, December 8, 2025 USPD - CPIMP - Rekt 

 read this article also in : 

 Top-tier audits? Check. Rigorous unit testing? Check. 

 A hacker living rent-free in your admin slot for nearly three months? Unfortunately, also check. 

 USPD didn't just drop the ball; they let someone else catch it before the game even started.

 On December 4th, roughly $1 million vanished - 98 million USPD minted out of thin air, 232 stETH drained , and a protocol left holding nothing but excuses and a 10% bounty offer .

 The attack didn't require breaking down the door; it simply involved walking in while the contractors were still installing the frame.

 By front-running the proxy initialization back on September 16th , the attacker installed a "shadow" regime that sat dormant for 78 days, forwarding legitimate calls to the audited code while Etherscan unknowingly displayed a facade of security .

 The protocol functioned perfectly, the audits were technically correct , and yet the admin keys belonged to a thief the entire time. 

 When your "verified" source code is just a decoy for an invisible middleman who moved in on day one, are you really decentralized, or just delusionally secure? 

 Credit: Peckshield , USPD , CertiK , Phantom Security , Dedaub , Blockscope , AstraSec , Emmet Gallic , Cryptonomist , ilemi , HokaNews , Blockthreat , Mladenov 
 Tis the season for giving, and USPD started December by wrapping up a $1 million stocking stuffer for the stranger living in their proxy. 

 USPD's $1 million loss barely registers on Rekt's leaderboard , but dismissing it as small-time would be missing the plot entirely.

 This wasn't some forgotten function or an under-tested edge case. 

 USPD got hit by CPIMP - Clandestine Proxy In the Middle of Proxy - an attack vector that security researchers had already exposed , documented, and largely neutralized back in July 2025. 

 Dedaub, Venn Security, and SEAL 911 spent 36 hours in a coordinated war room this past summer, racing to patch infected contracts across different chains.

 They saved over $10 million and notified dozens of protocols - Kinto, Pendle, GMX, Texture, Peapods.

 But USPD? Somehow missed the memo.

 While everyone else was getting inoculated, USPD was busy launching with a backdoor already installed, blissfully unaware that the front door had been left wide open since day one. 

 When the security community hands you the playbook for stopping an attack four months early, how exactly do you still end up as the case study? 

## The Skeleton Key

 September 16th, 2025. USPD's deployment day. 

 Most protocols treat proxy deployment like a two-step dance - deploy the contract, then initialize it. Simple, clean, atomic. 

 Except USPD decided to split the choreography.

 Deploy in one transaction, initialize in another. That gap - those precious seconds between steps - became a window wide enough for someone to slip through and claim the throne before the rightful owner even walked into the room.

 The window wasn't theoretical - it was brutally real according to the findings of ilemi from the herd .

 9:01:59 AM : proxy deployed.

 9:02:11 AM : attacker initialized.

 9:02:35 AM : USPD's legitimate initialization finally arrived, 24 seconds too late.

 Twenty-four seconds. Not days of negligence, not hours of oversight - just 24 seconds between deployment and someone else claiming the throne.

 Front-runners don't hesitate, and they certainly don't wait for your deployment script to finish.

 The attacker spotted USPD's pending initialization sitting in the mempool like an unlocked car with the keys in the ignition. One Multicall3 transaction later, they'd front-run the legitimate setup and seized admin rights while USPD's deployment script was still loading.

 But here's where amateur hour ends and professional tradecraft begins. 

 Rather than immediately draining everything and vanishing - the move that gets you caught and blacklisted within hours - the attacker installed a shadow proxy that forwarded every single call to USPD's legitimate, audited implementation . 

 Users interacted with the real code. Auditors verified the real logic. Everything worked exactly as intended.

 Meanwhile, the attacker manipulated event payloads and spoofed storage slots - Etherscan happily displayed the audited contract while the actual implementation sat somewhere else entirely. Green checkmarks. Verification passes. The proxy pointed to... well, technically it pointed to the attacker's middleman, but nobody was checking that closely.

 Normal proxy calls show one delegatecall in transaction traces - from proxy to implementation.

 CPIMP infections show two: proxy delegates to the malicious middle, which then delegates to the legitimate code. The signature was right there in every transaction, visible to anyone who knew transaction traces could lie. 

 But the real genius? 

 Self-restoration . After delegating each call to the legitimate implementation, the CPIMP would rewrite itself back into the implementation slot before the transaction finished. Try to upgrade away from it? It just reinstalls itself. The ultimate digital squatter with a lease that rewrites itself every time you try to serve eviction papers.

 The attacker understood exactly how Etherscan verifies implementations .

 Block explorers don't just trust events - they query the EIP-1967 storage slot that should contain the implementation address. By spoofing those exact storage reads, the shadow contract remained concealed while Etherscan showed only the legitimate code.

 For 78 days, USPD operated with perfect functionality while the admin keys sat in someone else's pocket. 

 September 17th - one day after infiltration - the attacker made their only other move before the finale: granting privileged roles to a secondary contract under their control . 

 Then? Radio silence. No suspicious transactions, no obvious red flags, just patience.

 December 4th finally rolled around, and the attacker decided it was showtime.

 Upgrade the proxy to a version that allows unlimited minting. Deposit 3,122 ETH as collateral. Mint 98 million USPD against it - roughly 10x what the collateral should permit . Drain 232 stETH . Dump the minted USPD into Curve for $300K USDC . Exit stage left with $1.05 million sitting in the drainer wallet. 

 When the attack playbook requires more patience than most legitimate development cycles, who's really playing the long game here? 

## Follow the Stolen Loot

 The attacker didn't exactly cover their tracks - they just made them extremely easy to follow. 

 Back in September, the front-running operation was handled by " The Infector " - planting the initial backdoor and granting privileged roles before vanishing into dormancy. 

 The Attacker’s Infector Address: 
 0x7C97313f349608f59A07C23b18Ce523A33219d83 

 The September infection was methodical - one transaction to claim admin rights, another to grant privileges, then silence.

 Front-Running Transaction Where Role Was Granted (Sept 16): 
 0xc0b7e490caac2b8cfa5e62d1b28a5e7dba7600e623c71352acbc9b23c2b65b7c 

 September 17th - one day after infiltration - the attacker made their only other move before the finale: granting privileged roles to a secondary contract under their control.

 Privilege Grant Transaction (Sept 17): 
 0xf9a493f061fbf17fe2cf7c26d6b03d85c6b43026500e61728933c2e218581079 

 Then? Radio silence. No suspicious transactions, no obvious red flags, just patience.

 Once the sleeper woke up, the party moved to "The Drainer."

 The Attacker's Drainer Address: 

 0x083379BDAC3E138cb0C7210e0282fbC466A3215A 

 The Attack Transaction on December 4th: 

 0xa7cab072bf0453301a0ab1b06c49a9405d115824fc617fb42cba9b70f3b893c2 

 This is where the party happened. The December 4th execution saw 98 million freshly minted USPD tokens and 232 stETH flow into this wallet.

 Roughly $300K worth of USPD got converted to USDC through Curve , while the rest sat waiting. 

 The attacker executed upgradeAndCall - simultaneously replacing the proxy's implementation with malicious logic and executing the exploit in a single atomic operation. 

 The new implementation allowed them to mint USPD ten separate times using the exact same 3,121.95 ETH collateral for each operation, generating roughly 9.8 million USPD per mint cycle.

 By the time the transaction finished executing, they'd created 98 million tokens against collateral that should have backed less than 10 million.

 Then came the drainage - 237 stETH pulled from protocol reserves across multiple addresses, followed by dumping the fraudulent USPD into Curve pools for $300,000 in USDC. 

 At time of writing, approximately $1.01 million remains parked in the attacker's address - not laundered through Tornado Cash, not split across a dozen wallets, just sitting there like someone's waiting for something.

 Maybe they're weighing USPD's 10% bounty offer . Maybe they're waiting for heat to die down. Maybe they're just that confident nobody can touch them anyway.

 The blockchain doesn't judge, doesn't reverse and doesn't respond to help tickets. 

 When your stolen million sits in plain sight on a public ledger and nobody can do anything about it, what exactly is the point of "flagging" addresses? 

## The Checkbox Theater

 USPD's official response hit Twitter at 10:40pm UTC on December 4th , and the playbook was textbook crisis management. 

 "URGENT SECURITY ALERT" - because nothing says controlled situation quite like all caps and alarm emojis . 

 " This was not a flaw in our smart contract logic ."

 Technically true. The code itself was fine. The audits from Nethermind and Resonance verified exactly what they were supposed to verify - the logic worked as intended.

 But here's where things get interesting.

 Auditors review code in repositories. They check the math, validate the logic flows, test the access controls as written. Nethermind and Resonance did exactly that - they certified the recipe . 

 What they didn't do? Watch the kitchen while it was being cooked. 

 The malicious proxy never existed in the codebase. It was injected live during deployment , meaning the auditors never saw it, never tested it, never had a chance to flag it. The attack didn't exploit the code - it exploited the deployment process.

 So when USPD says " rigorous security audits by top-tier firms ," they're technically correct. The audited code was secure.

 The deployment? That's where nobody was looking. 

 Astrasec spelled it out after the attack - "always ensure proxy deployment and initialization occur in the same transaction to prevent front-running risks." 

 The question isn't whether auditors should catch this - it's whether deployment procedures were even in scope to begin with.

 Either way, "we passed the audit" becomes the ultimate participation trophy when the attack vector was documented, actively exploited in the wild, and completely preventable.

 The team's explanation leaned heavily on CPIMP being this cutting-edge, nearly impossible to detect attack vector. "Highly sophisticated," they called it. "Emerging and complex."

 Except security researchers had documented, analyzed, and actively mitigated this exact attack four months earlier. Dedaub published detailed breakdowns . Venn Security and SEAL 911 saved dozens of protocols in a 36-hour war room . The playbook was public, the warnings were clear. 

 USPD offered the standard white-hat negotiation - keep 10%, return 90% , we'll drop all law enforcement involvement and call it a bug bounty. 

 At time of writing, the attacker hasn't responded to the bounty offer. The funds sat untouched over the weekend. The bounty offer hung in the air like an unanswered text.

 Then Monday December 8th rolled around and suddenly 330 ETH had been moved through Tornado Cash by the attacker . So they may have made their decision.

 4 days after the attack, USPD emerged with their recovery playbook : V2 launching Q2 2026, claim tokens for affected holders, a dedicated recovery pool funded from protocol revenue, and an exclusive wallet-gated Telegram group for the 230 victims.

 The promise ? Make holders whole before any other allocation. The reality? Another six months minimum before anyone sees a dollar, assuming V2 actually launches and generates revenue to fund that recovery pool. 

 "Rebuilt from ground up" hits differently when the ground up is still a smoking crater. 

 Simplified architecture, DeFi-compatible yield design, privacy integration - all lovely features for a protocol that somehow missed the memo about atomic deployment after security researchers spent 36 hours in July saving everyone else.

 Meanwhile, USPD's stablecoin maintained its peg - a minor miracle considering 98 million unbacked tokens were minted. Trading volume dropped 20% to around $2.56 million , but the dollar peg held steady.

 Small mercies in a situation with precious few of them. 

 When your defense is "the code we showed the auditors was clean," you're admitting nobody verified what actually got deployed - and if audits don't cover the moment your protocol goes live, what exactly are we auditing? 

## What Everyone Else Saw Coming

 USPD wasn't even original in getting owned this way. 

 Kinto Protocol wrote the exact same story earlier this year : March 19th deployment at 20:24:40, attacker initialization two seconds later at 20:24:42, $1.55 million gone on July 10th when patience finally ran out. 

 Two seconds. Not 24 - two. The same CPIMP framework, the same patient waiting game, the same inevitable conclusion.

 The July war room that saved dozens of protocols apparently missed both Kinto and USPD, despite the infections being visible on-chain for anyone running the right queries.

 As ilemi from the Herd pointed out : "24 seconds between attacker and team transactions. This alone should have been a huge red flag... but this data is not easy to find or see unless you know how to write Dune queries."

 The data was all on-chain. The red flags weren't obvious unless you knew where to look. 

 But here's the more uncomfortable truth that auditor 0xmladenov spelled out: "Deployment steps are often marked out of scope in audits with the assumption they'll be handled later, and too often they're not."

 Translation? Auditors checked every line of code while explicitly not checking the one moment that actually mattered - when that code went live. The recipe was perfect; nobody watched the kitchen while it was being installed.

 Nethermind and Resonance did exactly what they were hired to do. The deployment? That was someone else's problem, right up until it became everyone's problem. 

 When dozens of protocols get saved in July and you launch in September still vulnerable to the exact attack everyone just survived, who's really responsible for due diligence? 

 USPD got robbed in slow motion, and everyone watched it happen in real-time without knowing it. 

 The attacker didn't break anything - they just claimed the keys before anyone else thought to check if the locks were installed. 

 Seventy-eight days of perfect operation, flawless functionality, and glowing audit reports while someone else held admin rights the entire time.

 July's CPIMP war room saved dozens of protocols and over $10 million, yet USPD launched months later without checking if their front door was even attached.

 Their "rigorous audits" checked every line of code while nobody verified what actually got deployed to mainnet.

 Now $1 million sits in plain sight on a public blockchain, the attacker hasn't said a word, and USPD's stablecoin inexplicably maintains its peg like everything's fine. 

 When the security community hands you a four-month head start and you still end up as the cautionary tale, are we securing protocols or just auditing participation? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

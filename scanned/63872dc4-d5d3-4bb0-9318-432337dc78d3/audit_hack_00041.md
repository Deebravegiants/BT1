# [H] BetterBank exploit: $5 million vanished from PulseChain's lending protocol when an attacker exploited the bonus minting system with surgical precision - creating fake liq

## Summary
Severity: High
Target: BetterBank
Loss: $5,000,000
Published: 8/26/2025
Source: https://rekt.news/betterbank-rekt
Type: rekt-postmortem

## Details
## BetterBank - Rekt

 Thursday, August 28, 2025 BetterBank - Reward Logic Flaw - Rekt 

 read this article also in : 

 Six weeks. That's how long BetterBank had been promising "better" DeFi before someone decided to test their definition of the word. 

 $5 million vanished from PulseChain's lending protocol when an attacker exploited the bonus minting system with surgical precision - creating fake liquidity pairs, harvesting infinite rewards, and draining real assets while the team watched their "revolutionary" math crumble in real time. 

 The exploit wasn't sophisticated - just basic LP manipulation that any security researcher could spot.

 What made it devastating was BetterBank's decision to downgrade their auditor's critical warnings to "low priority" because the test scenarios didn't match their narrow expectations.

 While genuine users got rekt, mysterious wallets appeared at the crash's exact bottom, scooping up discounted tokens like they'd been waiting for the fire sale.

 The attacker even returned 550 million pDAI - a gesture of goodwill that's about as common in DeFi as honest tokenomics.

 Zokyo had flagged the vulnerability, BetterBank had dismissed it as low/informal , and somewhere between those two positions lay $5 million in user funds. 

 When your auditor screams "fire" but you're too busy admiring the smoke, who exactly is responsible for the ashes? 

 Credit: MiTrade , zokyo , BetterBank , Chaofan Shou , Bitcoin World 
 BetterBank's Monday morning started like any other - until someone started draining their protocol faster than they could tweet damage control. 

 Within minutes of detecting the exploit, the team emergency-paused the protocol and scrambled to assess the carnage while their "revolutionary" bonus minting system got turned into a money printer for someone else.

 The attacker found BetterBank's fatal design flaw - bonus minting that handed out free ESTEEM tokens whenever someone bought Favor, supposedly to reward legitimate trading.

 Legitimate was never properly defined.

 Chaofan Shou broke down the mechanics : anyone could create their own LP on PulseX using BetterBank's registered FAVOR token, perform bulk swaps to harvest massive bonuses, then convert those rewards into real money. 

 The attacker didn't need to break anything - they just built their own liquidity pool using one legitimate token (FAVOR) and one worthless token they controlled. 

 BetterBank's systems saw Favor trading and started printing bonus tokens like a broken ATM .

 Pure bulk swapping should have triggered devastating tax penalties - 50% fees that would make any dump economically suicidal.

 Problem was, BetterBank's tax logic only applied to pairs they had blessed as "official."

 Homemade LPs got the royal treatment - zero taxes, maximum rewards.

 The mathematics were brutally simple: infinite bonus generation minus zero taxes equals protocol death spiral. 

 When smart contracts can't tell the difference between legitimate and counterfeit liquidity, what exactly are they securing? 

## The Money Trail

 BetterBank's nightmare began with a wallet that didn't exist until it needed to steal $5 million. 

 Primary Attacker Address: 
 0x48c9f537f3f1a2c95c46891332E05dA0D268869B 

 The funding trail led back to Tornado Cash - the attacker's ETH wallet was originally seeded with about $450 through the mixer, suggesting premeditation rather than opportunistic discovery.

 Tornado Cash Funding: 

 0x64637619d3052ed3350402ca0a821eb907c34836c381a91ee8041a90ddad20c3 

 The attacker had a gameplan - they built their own exploit infrastructure first. 

 Three custom contracts deployed by the primary attacker address formed the attack's backbone: 

 0x767C5a70CDa0D9469ccE3a56653E1d170D9849c3 

 0x792CDc4adcF6b33880865a200319ecbc496e98f8 

 0x18Dd9E3F039F319c854c389fC87b5295d3cb7f94 

 Each contract served a specific purpose in the coordinated attack infrastructure , working together to exploit BetterBank's reward system and bypass its security mechanisms. 

 The attacker had essentially built their own parallel financial system that BetterBank's protocols couldn't distinguish from legitimate activity. 

 Once the vault was empty, it was time to disappear.

 The stolen assets didn't stay put. Everything got swapped for ETH, bridged to Ethereum, then funneled toward Tornado Cash - the money laundering service of choice for those who prefer their transactions permanently scrambled.

 The attacker managed to convert roughly 309 ETH , though some reports suggested 215 ETH in the initial conversion.

 Most telling was what happened next - instead of vanishing completely, the attacker returned 550 million pDAI to the protocol . 

 When thieves start returning more than half their loot voluntarily, are they really thieves at all? 

## Screaming into the Void

 Three months before BetterBank went live, Zokyo flagged two related risks in their audit findings. 

 Issue 1 involved flash loan exploitation of the Favor Bonus system , while Issue 2 highlighted how malicious users could exploit Favor Bonus using bogus tokens via the UniswapWrapper by deploying their own contract and LP. 

 Zokyo laid out the attack path step-by-step - exactly the method that would later gut the protocol for $5 million.

 BetterBank read the report and made their call: downgrade to "Low. "

 The justification was breathtaking in its precision.

 Zokyo's test used legitimate tokens like ETH instead of worthless junk , producing negative yields in the demo environment. 

 Since the proof-of-concept didn't perfectly mirror a real attack, BetterBank decided the vulnerability wasn't worth fixing. 

 Zokyo warned about bogus tokens destroying the protocol. BetterBank fixated on test ETH producing negative returns.

 In other words, the audit’s scope and assumptions gave BetterBank plenty of room to convince themselves the protocol was safe - turning a documented risk into a convenient comfort blanket.

 The $5 million gap between those two interpretations would later become very real user losses.

 Post-exploit, both sides pointed fingers.

 Zokyo admitted their communication "could have been clearer." BetterBank maintained they "never saw the true danger" of the exact attack vector Zokyo had documented. 

 But when your security team finds the smoking gun and you decide it's just a cap pistol, what exactly did you think would happen when someone loaded real bullets? 

## Strange Bedfellows

 Take this with a grain of salt - what follows are observations that might mean everything or nothing at all. Red flags that could be coincidences, patterns that might be paranoia. 

 But in a space where trust is the only currency that matters, some questions deserve asking. 

 Maybe it was just a coincidence, but the timing felt a little too perfect.

 BetterBank had been live for 3 weeks when the exploit hit - long enough to build serious TVL, short enough that most users hadn't developed deep loyalty or conducted thorough due diligence.

 The attack itself raised eyebrows.

 Sure, the LP manipulation was textbook DeFi exploitation, but returning 550 million pDAI?

 That's not standard operating procedure for hostile actors who typically dump everything and vanish. 

 Could this have been some kind of negotiated "white hat" scenario? 

 The team's announcement suggested they'd reached "successful parley with the exploiter" - language that sounds more like diplomacy than victimization.

 Speaking of the team, some background digging raises its own questions.

 The co-founder's background might be worth a look. LBdefi's Twitter bio lists co-founder roles at Solidus Money and Grape Finance - both projects have been relatively quiet lately. 

 Solidus Money shows no recent social media activity, while Grape Finance hasn't posted since 2023 . 

 Maybe the projects never had a chance to get off the ground. Maybe they still will…

 BetterBank looks to be sticking around, for now.

 They even had to take to Twitter to claim they did not rug and were indeed hacked .

 The partial return of stolen assets shows that even in chaos, outcomes aren’t always clear-cut - and sometimes timing alone tells half the story. 

 In a system built on code, who really holds the advantage - those writing the rules or those reading the loopholes? 

 Six weeks of "better" banking ended with the oldest lesson in DeFi: the house always wins, especially when it might be playing both sides of the table. 

 BetterBank promoted themselves as revolutionary finance but delivered textbook exploitation - fake LPs, infinite minting, and a tax system that couldn't tell legitimate from counterfeit. 

 The technical failure was embarrassing enough, but the behavioral patterns surrounding the "exploit" tell a much more interesting story.

 Auditors screamed fire, teams ignored smoke detectors, and somewhere between critical warnings and convenient dismissals, $5 million in user funds found new homes.

 Sometimes the left hand and the right hand just don’t sync up.

 When auditors flag risks and teams misinterpret them, warnings can get lost in translation - and in DeFi, even small misunderstandings can cost millions. 

 In Zokyo’s own words , their “communication fell short.” 

 Even when intentions are good, missteps in communication can ripple into real-world losses.

 The partial return of stolen assets might look like mercy, but in a space where exit liquidity is the real product, yesterday's victims become tomorrow's bag holders.

 DeFi exploitation math is brutally simple: find hole, drain funds, blame hackers.

 What's getting creative is the show that follows - turning inside jobs into "sophisticated attacks" and coordinated exits into heartwarming "white hat recoveries."

 PulseChain's hottest protocol learned that revolutionary technology still runs on ancient human psychology: greed, deception, and the eternal search for someone else to hold the bag. 

 When the revolution gets televised but the revolutionaries keep the cameras, who exactly are we supposed to trust with the remote? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

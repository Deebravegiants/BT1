# [H] New Gold Protocol exploit: 299 followers and a "security is non-negotiable" tweet 3 days prior - New Gold Protocol's entire legacy before becoming Tuesday's bloodbath

## Summary
Severity: High
Target: New Gold Protocol
Loss: $2,000,000
Published: 9/17/2025
Source: https://rekt.news/newgold-protocol-rekt
Type: rekt-postmortem

## Details
## New Gold Protocol - Rekt

 Friday, September 19, 2025 New Gold Protocol - Price Manipulation - Rekt 

 read this article also in : 

 299 followers and a "security is non-negotiable" tweet 3 days prior - New Gold Protocol's entire legacy before becoming Tuesday's bloodbath. 

 September 17th brought fresh carnage to BNB Chain as this freshly minted protocol hemorrhaged $2 million through vulnerabilities so obvious that even script kiddies would blush 

 Flash loans, price oracle stupidity, and transfer logic written by someone who apparently skipped smart contract kindergarten - NGP speedran every possible way to get rekt.

 Twitter promised transparency and automated burns.

 Smart contract delivered automated theft and transparency about how incompetent the devs were. 

 Flash loan some USDT, manipulate the PancakeSwap pool reserves, bypass their pathetic buying limits by sending tokens to the dead address , then watch their broken fee mechanism sync the pool into oblivion.

 444 ETH vanished into Tornado Cash faster than NGP's credibility.

 Token cratered 88% . The protocol has remained radio silent since the incident. 

 When your protocol works flawlessly for hackers but catastrophically fails users, what exactly were you building? 

 Credit: New Gold Protocol , The Block , BitcoinEthereumNews , Blockaid , Peckshield , CertiK , William Li 
 Blockaid's exploit detection system caught the carnage first - “multiple malicious transactions targeting NGP on BSC”, with roughly $2 million drained. 

 Real-time monitoring turned into a live autopsy as security firms rushed to explain how spectacularly NGP had failed.

 PeckShield confirmed the obvious hours later : "$NGP token from newgoldprotocol was exploited for ~$2M."

 Token down 88% in an hour , stolen funds already washing through Tornado Cash.

 Meanwhile, New Gold Protocol's Twitter account ? Complete radio silence. 

 No acknowledgment, no damage control, no "we're investigating" platitudes. 

 Just the digital equivalent of hiding under a rock while security firms dissected their corpse in public.

 Even 24 hours later, NGP couldn't muster a single tweet about losing $2 million of other people's money.

 They were still promoting their launch , like they were living in an alternate reality.

 Ironically, on September 14th, they posted that : "Security is non-negotiable." 

 Apparently neither is staying silent when your non-negotiable security gets negotiated away for $2 million? 

## Turning $211 Million into $2 Million

 NGP's code was a fine example in writing the worst possible smart contract. 

 Two catastrophic flaws that any competent developer would catch in five minutes of testing, but somehow made it to mainnet. 

 Two fatal flaws working in perfect harmony: a getPrice() function that trusted PancakeSwap reserves like gospel, and transfer logic so broken it made the exploit trivial.

 Price oracles 101: never rely on a single DEX pool's reserves for pricing.

 Attackers can manipulate those numbers with flash loans faster than you can say "rug pull."

 NGP apparently skipped that lecture. 

 The attack script was embarrassingly simple. 

 Flashloan $211 million , dump it into the mainPair pool to crash NGP reserves and inflate the USDT side.

 Now getPrice() thinks NGP is worthless , letting the attacker bypass maxBuyAmountInUsdt limits by buying massive amounts of tokens.

 But here's where NGP's incompetence really shines: their transfer function included a "fee mechanism" that deducted 35% from the pool balance whenever someone sold, then called sync() to update reserves.

 This wasn't a feature - it was a self-destruct button waiting to be pressed. 

 The attacker bought NGP tokens earlier with multiple accounts , then used the manipulated pricing to acquire even more tokens by setting the recipient address to the "dead" address - conveniently whitelisted to bypass buying restrictions. 

 Finally, they dumped all their NGP tokens, triggering that transfer logic mechanism that reduced the pool's NGP reserves from 477,000 to 0.035 tokens .

 When you reduce token reserves by 13.6 million times , you don't just break the AMM's x*y=k invariant - you obliterate it.

 Pool drained, attack complete, protocol dead. 

 What happens when your smart contract's biggest security feature is teaching attackers exactly how to rob you? 

## Following the Breadcrumbs

 Tornado Cash funded the wallet that killed NGP. Classic move - mix your ETH, bridge to BNB Chain, then go shopping for vulnerable protocols. 

 Tornado Cash Funding (September 10th): 

 0x31b80cf3b477948fb47a03aa5ecb8a9e30b99840e59af8959e5797c1ea4cd3a3 

 Exploiter Address: 

 0x0305ddd42887676ec593b39ace691b772eb3c876 

 Attack Transaction: 0xc2066e0dff1a8a042057387d7356ad7ced76ab90904baa1e0b5ecbc2434df8e1 

 September 17th, 7:02 PM UTC - NGP went from "promising new protocol" to "expensive lesson" in a single transaction. 

 Flash loan secured, reserves manipulated, limits bypassed, pool drained. All the stolen USDT got swapped to ETH and bridged back to Ethereum mainnet. 

 Ethereum Address: 

 0x8618314270528e245fbbb6fba54e245bb61a8d47 

 444 ETH was methodically fed into Tornado Cash's tumble cycle.

 The attacker didn't rush - they broke down the haul into digestible chunks over 10 minutes.

 Almost twenty separate deposits into Tornado Cash's mixer pools: 0.1 ETH, 1 ETH, 10 ETH, and 100 ETH increments.

 Standard Tornado Cash denominations, but the systematic approach suggests someone familiar with the mixing process.

 They didn't reinvent the wheel, just found a protocol dumb enough to let them use it. 

 When your exploit gets traced by every major security firm but your protocol can't even acknowledge it happened, who really got played? 

## The Road to Nowhere

 NGP's five-year roadmap promised "AI-powered contract auditing improves security" by 2026. 

 Apparently they planned to wait three years before bothering with basic security measures. 

 Their whitepaper reads like fever dream economics mixed with ChatGPT hallucinations:

 "Native DEX with automated matching," "Layer 2 testnets," "Aurora AI v2 enables automated fund management" - all scheduled for 2026 while their 2025 launch couldn't handle basic price feeds.

 Even their resources page screams amateur hour . Documentation hosted on Google Drive?

 Professional protocols use proper hosting, version control, and redundancy. NGP used free cloud storage like a college student sharing homework. 

 The protocol that promised to build an " intelligent civilization " couldn't figure out how to prevent flash loan attacks that script kiddies master in weekend hackathons. 

 Their roadmap talks about AI-powered auditing while their current code suggests they've never heard of human-powered auditing.

 Three days of security promises, hours of actual uptime, and years of grandiose plans that will never see mainnet.

 NGP managed to speedrun the entire lifecycle of a failed protocol - hype, launch, exploit, silence, irrelevance. 

 When your protocol's biggest achievement is teaching others what not to do, was building it ever the point? 

 Radio silence isn't just NGP's Twitter strategy - it's their entire community management playbook. 

 Over 24 hours since losing $2 million and their Telegram channel reads like nothing happened. 

 No team announcements, no damage control, no panicked community members demanding answers.

 The chat logs show regular activity but zero mention of the $2 million hack.

 NGP created the perfect echo chamber - a community so detached from reality that a $2 million exploit doesn't even register as newsworthy. 

 Maybe staying quiet worked for their 299 Twitter followers, but ignoring catastrophic security failures doesn't make them disappear.

 While security firms dissected their code and traced their stolen funds across multiple blockchains, NGP's team apparently decided the best crisis management strategy was pretending the crisis never existed.

 Their roadmap promised an intelligent civilization by 2030 , but they couldn't even manage intelligent damage control for 48 hours. 

 If your protocol gets rekt in DeFi but nobody in your community talks about it, did the exploit really happen? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

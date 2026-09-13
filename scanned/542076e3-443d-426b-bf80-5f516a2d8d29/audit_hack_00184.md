# [H] Odin.Fun exploit: 58.2 Bitcoin vanished in under two hours on August 12th as Odin.fun suffered its third major security breach in six months

## Summary
Severity: High
Target: Odin.Fun
Loss: $7,000,000
Published: 8/12/2025
Source: https://rekt.news/odin-fun-rekt
Type: rekt-postmortem

## Details
## Odin.Fun - Rekt

 Friday, August 15, 2025 Odin.Fun - ICP - Bitcoin Defi 

 read this article also in : 

 58.2 Bitcoin vanished in under two hours on August 12th as Odin.fun suffered its third major security breach in six months. 

 Bob Bodily's "world's fastest Bitcoin token trading" platform promised revolutionary speed and security, but delivered something else entirely - a $7 million lesson in how liquidity manipulation attacks work. 

 Hackers pumped worthless SATOSHI tokens through Odin's AMM, artificially inflated prices, then drained real Bitcoin while the founder's PhD-level engineering watched helplessly from the sidelines.

 This wasn't Odin's first rodeo with disaster - March brought deposit synchronization bugs , April saw Bodily's personal account reportedly compromised for $178K, and now August delivered the coup de grâce.

 Treasury insufficient to cover losses, trading suspended indefinitely, compensation plans stuck in permanent "coming soon" mode. 

 Pattern recognition suggests Odin.fun has perfected the art of losing user funds every two months - so what separates legitimate security failures from something more calculated? 

 Credit: The Block , Peckshield , Bitget , NameCoin News , Bob Bodily , decrypt , CoinDesk , Cybertechwiz , crypto.news , businessman.eth , Cryptopolitan , CertiK , Halborn , Coin Edition , Binance , Radiant Capital , DeltaPrime 
 Bob Bodily's morning started normally on August 12th. It didn't stay that way. 

 Then came the first damage control Tweet : "Hi everyone - we're looking deeper into the recent withdrawals from the platform, so we've paused trading to ensure we can protect user funds,"

 Classic crypto speak for "we're getting rekt and don't know how to stop it."

 Platform Bitcoin reserves hemorrhaged from 291 BTC to 232.8 BTC while Bodily crafted his corporate non-response. 

 PeckShield rang the alarm bells , confirming what the on-chain data already screamed: hackers had systematically emptied Odin's liquidity pools with mathematical precision. 

 The attack vector reads like a DeFi exploit tutorial . Deposit worthless SATOSHI tokens, manipulate AMM price ratios without external validation, withdraw at inflated rates, walk away with real Bitcoin.

 Odin's freshly updated AMM trusted its own internal math more than market reality - a decision that cost users $7 million in under 2 hours.

 Eight hours of radio silence followed while 58.2 Bitcoin found new homes across multiple wallets, each transaction a permanent reminder of Odin's security theater. 

 When fresh coordinated attacks hit with surgical precision while security experts call the vulnerability "inexcusable" for someone with Bob's background, who's really getting schooled here - the hackers or the users? 

## Textbook Manipulation

 The August carnage followed one of DeFi's oldest tricks in the book, executed by someone who'd clearly done their homework on Odin's weak spots. 

 Deploy worthless tokens , manipulate AMM price ratios , cash out with real Bitcoin while leaving digital confetti behind. At least, that's how it looked on the surface. 

 PeckShield tracked the carnage to two primary attacker addresses ( Odin.fun operates on Internet Computer Protocol, using ICP principals as user IDs rather than traditional blockchain addresses):

 First Account aka Fresh Attack: 

 Urguz-m32zo-jlld6-pyy4l-z3c24-jv4pt-5fmll-gq2xd-6siiz-oxkao-xae 

 Second Account aka Sleeper Cell: 
 jeypm-z6t4p-uqshx-dtay4-qgw5d-ca7j5-alviu-fch2d-nmsnc-c4k3k-aae 

 But the attacker addresses tell a much darker story than random opportunists stumbling onto a vulnerability.

 The first account ("Fresh Attack") was created on August 12th just one hour before Bob Bodily announced the platform suspension. Fresh wallet, immediate funding, surgical execution. Purpose-built for the heist.

 The second account ("Sleeper Cell") reveals something far more sinister: created on June 20th, made small SATOSHI token purchases, then went completely dormant for 53 days. A sleeper cell, planted and waiting.

 On August 12th, the dormant account suddenly reactivated. Twenty-three minutes later, the fresh account appeared with funding. 

 Coincidence? In crypto, maybe. In criminal coordination? Definitely not. 

 Both accounts are still active on Odin.fun, their complete transaction histories sitting there like confessions waiting for someone to read them.

 Every manipulation cycle documented: buy tokens, add liquidity, inflate prices, extract Bitcoin, repeat.

 The Sleeper Cell account focused on SATOSHI tokens - exactly what PeckShield identified as the primary attack vector.

 The Fresh Attack account hit ODINPEPE and multiple other tokens simultaneously.

 This wasn't some degen stumbling onto a vulnerability during their morning coffee. 

 Months of planning, split-second coordination, systematic execution - someone did their homework while Bob was busy tweeting about revolutionary Bitcoin DeFi. 

 The vulnerability itself wasn't unique - just basic AMM manipulation that other DeFi protocols have seen before.

 Odin's AMM math trusted its own price calculations more than reality - always a winning strategy in DeFi.

 Empty liquidity pools with fresh deployments? Might as well hang a "free money" sign on the front door. 

 Multiple fresh accounts hit the same exploit pattern while Bob's security team practiced their surprised Pikachu faces. 

 Fund shuffling through intermediary wallets before cashing out - professional work from someone who'd clearly studied the playbook.

 The vulnerability wasn't exactly cutting-edge. Midas Capital got rekt twice in 2023 due to similar AMM manipulation . Hundred Finance joined the AMM manipulation party the same year. Post-mortems got published. Solutions got documented.

 But apparently reading those pesky security reports is optional when you're revolutionizing Bitcoin DeFi. 

 When the solutions to prevent AMM exploits were already published by security researchers, why did Odin's " top-tier security team " miss what every DeFi security researcher flagged as basic due diligence? 

## The China Excuse

 Bob's post-hack performance followed the well-worn script of crypto crisis management, with a few suspicious improvisations. 

 Eight hours of silence while Bitcoin moved across wallets, then the standard-issue mea culpa with a geopolitical twist. 

 "Several malicious users, primarily linked to groups in China, took advantage of this vulnerability to steal a significant amount of BTC from the platform," Bodily announced , conveniently deflecting blame to foreign actors.

 Classic move - when your code fails, blame state-sponsored hackers.

 Never mind that the exploit required no sophisticated techniques , just basic AMM manipulation any DeFi degen could execute.

 The "sophisticated" attackers Bob blamed apparently forgot basic operational security - they left complete transaction histories on Odin.fun's own platform for anyone to examine. Hardly the behavior of state-sponsored actors, more like criminals who didn't expect anyone to look.

 But hey, why focus on embarrassing operational failures when there's a treasury to discuss?

 Treasury can't cover the losses , but don't worry - " concrete plans " are coming. 

 Details? That's classified. Timeline? Soon. 

 Meanwhile, those "identified several groups who profited from the exploit" remain mysteriously unprosecuted despite Bob's tough-guy ultimatum: "You have a short window to return the funds before it is too late. This is not a negotiation."

 The alleged coordinated law enforcement response reads like bad theater. U.S. authorities contacted, Binance and OKX engaged with Chinese officials, blockchain forensics deployed.

 Impressive mobilization for a memecoin platform that launched six months ago and burns through user funds bimonthly.

 Most telling? Bob's unwavering confidence that Odin will rebuild stronger. "We believe the future of Bitcoin DeFi is massive, and we want you with us when we get there," he tweeted while millions in stolen Bitcoin sat untouched in attacker wallets. 

 When someone loses $7 million but sounds like they're pitching investors on the next big thing, what exactly are they really selling? 

## Bob’s Broken Record

 This wasn't Bob and Odin's debut on the disaster stage. March 7th brought deposit synchronization chaos - 74 BTC vanishing from user balances while corresponding mainnet transactions played hide and seek. 

 Technical glitch, no actual theft, problem resolved within hours. Standard growing pains for a February 2025 launch, or so the narrative went. 

 April 14th shattered that illusion . Bob Bodily's personal account got "hacked," liquidating $178,700 worth of assets in what was later attributed to errors in the "Sign-In With Bitcoin" authentication system .

 Trading halted platform-wide because apparently one compromised account threatened everyone's funds.

 ODINDOG crashed 50% as panic spread faster than Bodily's damage control tweets.

 Why suspend all withdrawals if only Bob's account was compromised?

 Six months, three security failures, and millions in losses later. Lightning doesn't strike the same spot three times by accident. 

 When your track record includes being "hacked" personally, blocking critics on social media, and consistently launching vulnerable code despite PhD-level credentials, where's the line between incompetence and intent? 

## The PhD Paradox

 Bob Bodily's credentials paint the picture of someone who should know better. 

 PhD in Educational/Instructional Technology from BYU, Co-Founder & CEO of Toniq Labs, Co-Founder & CEO of Bioniq Bitcoin Ordinals marketplace. 

 Legitimate technical background spanning blockchain development since 2021, with actual products shipped and functioning ecosystems built.

 Yet somehow this accomplished developer consistently deploys code that gets exploited by attacks so basic that anonymous DeFi experts mock them publicly.

 "Anyone having some knowledge on DEX pools would know this," s0xToolman from Bubblemaps told Decrypt about the August hack . "There's no excuse for the team to not know this could happen." Textbook AMM vulnerabilities that first-year smart contract students learn to avoid.

 Community warnings weren't subtle either. businessman.eth had been "warning people for months to get your funds off Odin Fun" before the August carnage. 

 His reward? Bob blocked him on Twitter. 

 Turns out businessman.eth was literally warning about accounts that were already positioned for attack - the Sleeper Cell account had been dormant with SATOSHI tokens for over a month when those warnings were issued.

 Raven Thorogood III's sarcastic post-mortem hit different : "Odin.fun launched 6 months ago and has had 3 legit hacks.

 Averaging a major hack every 2 months.

 Honestly impressive, just a few more multi million dollar hacks then up only."

 The timing raises eyebrows too. Bob launched Odin.fun in February 2025 , right as the memecoin casino reached peak frenzy.

 Abandoned his established ICP projects for quick-flip Bitcoin speculation plays. 

 When legitimate developers with proven track records repeatedly launch fundamentally broken code while silencing critics, are we witnessing incompetence or something more calculated? 

## Community Fracture

 Odin's user base imploded faster than their liquidity pools. 

 Bob's remaining cheerleaders clung to the "sophisticated attack" story, still believing in transparency and those eternally "coming soon" compensation plans. 

 Meanwhile, critics who'd been screaming warnings for months watched vindication unfold in real-time - too bad their Twitter accounts were blocked by the founder they'd tried to save.

 ODINDOG token crashed 50% before most holders could process what happened.

 Brutal for anyone, worse for the true believers who'd already eaten losses during April's "Bob got hacked" episode and doubled down on loyalty. 

 Getting rekt three times in six months builds character - specifically, the kind that questions every life choice leading to that moment. 

 The timing couldn't have been worse for true believers.

 Odin.fun had just celebrated breaking volume records in early April , with ODINDOG reaching second top Bitcoin token of ALL TIME based on volume .

 Success stories becoming cautionary tales overnight. 

 But three hacks in six months raises an uncomfortable question - is this astronomical bad luck, or does Odin belong to an even more exclusive club? 

## Serial Offenders Club

 Bob's post-hack theater hit all the classics: San Francisco meetings with "strategic partners," external reviewers onboarded, audit firms consulted. 

 Twenty-four hours later : "One audit underway. Smaller group, but fast and nimble" - translation: the big firms quoted timelines longer than Odin's runway. 

 Speaking of audits - Odin.fun's website contains zero documentation, no security audits, no technical papers. Just links to Twitter and Discord.

 Even CertiK's project page shows no completed audits. Revolutionary security through obscurity, apparently.

 FBI involved, blockchain wizards deployed , "strategic partners" incoming. Quite the avengers for a memecoin platform that burns through user funds bimonthly.

 "The ODIN•FUN community is the most incredible community in all of crypto," Bob gushed while that same community watched their funds disappear for the third time in six months. 

 Odin.fun joins crypto's most exclusive club - protocols that turned repeat exploitation into an art form. 

 Welcome to the serial victims' leaderboard, where second chances become third strikes and "lessons learned" means "vulnerability patterns repeated."

 There were two exploits as Midas Capital back in 2023 ( $660K , then $600K ), rebrand to Ionic, immediately get social engineered for $6.9M by fake Lombard Finance representatives.

 Then after rebranding, they got rekt again under their new name - Ionic Money back in February of this year .

 Three strikes spanning multiple years, each time promising better security while delivering worse outcomes. 

 Maybe the third time is a charm... but in this case, it’s more like 'third strike, you're out. 

 Onyx Protocol achieved something even more impressive - back-to-back exploits using the identical Compound v2 vulnerability.

 $2.1M in the first hack in 2023, $3.8M in the 2024 sequel , same attack vector both times.

 Security researchers literally published the fix between exploits , yet Onyx deployed new markets with the exact same fatal flaw.

 After the second hack, Onyx had to completely shut down and relaunch as a different protocol - the ultimate death spiral. 

 Radiant Capital got hit twice in 2024 - $4.5M to a known Aave fork bug , then $53M when their "robust" 3-of-11 multisig crumbled like wet cardboard. 

 Two hacks, same tired playbook. To their credit, Radiant actually launched a comprehensive remediation program with specific milestones, including 70% compensation for smaller deposits and a multi-pronged funding strategy.

 DeltaPrime speedran the disaster cycle in late 2024: $6M private key fumble , then $4.85M input validation face-plant just two months later.

 Peckshield had flagged both vulnerabilities beforehand , yet DeltaPrime shipped vulnerable code anyway.

 But here's the difference - DeltaPrime actually stepped up . 

 Founders sacrificed 33% of their token allocation, implemented a comprehensive compensation plan paying victims 140% of their losses through future revenue, and are currently working through $11M in total damages. 

 But Odin's trajectory stands out even among this distinguished company.

 Six months, three security failures, each time with Bob personally involved or affected.

 Others at least managed gaps between disasters. 

 What separates legitimate bad luck from platforms that have mastered the economics of staying barely afloat while bleeding user funds? 

 Six months, three hacks, zero accountability - Bob Bodily has achieved what most DeFi founders only dream about: staying relevant while consistently losing other people's money . 

 Odin.fun offered Bitcoin DeFi at warp speed but delivered a PhD thesis on how credentials can't fix fundamentally broken economics. 

 Incompetence or insider job? The results look identical either way: user funds vanishing on schedule while Bob tweets about bright futures and building together.

 Those concrete compensation plans have all the substance of vaporware - eternally in development, never quite ready for release.

 Treasury insufficient, timeline indefinite , but somehow the vision for Bitcoin's DeFi future burns brighter than ever.

 The attackers' user profiles remain active on Odin.fun as of now, complete transaction histories preserved like digital evidence in a criminal case that hasn't been filed yet.

 Maybe that's Odin's real innovation - proving that in crypto, reputation death is just another business model waiting to be monetized. 

 When the next memecoin launchpad promises "revolutionary security" and posts their founder's academic credentials, will anyone remember to ask how many times they've been "hacked" before? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [C] Humanity Protocol exploit: Humanity Protocol sold the world a palm scan and a promise - that in a sea of bots, AI slop, and synthetic identity, their blockchain could tell you w

## Summary
Severity: Critical
Target: Humanity Protocol
Loss: $36,400,000
Published: 6/8/2026
Source: https://rekt.news/humanity-protocol-rekt
Type: rekt-postmortem

## Details
## Humanity Protocol - Rekt

 Tuesday, June 16, 2026 Humanity Protocol - Private Key Leak - Rekt 

 read this article also in : 

 Humanity Protocol sold the world a palm scan and a promise - that in a sea of bots, AI slop, and synthetic identity, their blockchain could tell you who was real. 

 "The trust layer of the internet," founder and CEO Terence Kwok called it. Proof of Humanity, a self-described zero-knowledge Worldcoin competitor. 

 On June 8, 2026, someone walked through the front door using a stolen key, rewrote the rules of the protocol mid-game, and left with 447 million $H tokens, $36.4 million of which has already been confirmed moving through Uniswap .

 Three of six multisig keys, enough to cross the signing threshold, were later said to have been backed up to a compromised employee laptop. 

 No timelock stood between that threshold and absolute control . The attacker didn't break the code. They just became the admin.

 Within hours, ZachXBT was on X calling it a "crime pump" and demanding the team disclose their market maker agreements with a Hong Kong entity. 

 PeckShield was running the on-chain trail and arriving at a darker conclusion, one that would later call the incident not a hack at all, but a staged performance. 

 And banteg surfaced an on-chain message from the attacker to Chris Blec , a single sentence that exposed the state of Humanity Protocol's security more clearly than any post-mortem could.

 A project built to verify human identity couldn't secure its own keys. A foundation assembled to govern the trust layer of the internet had, as one of its founding directors, Mario Nawfal , one of crypto's most prolific hype merchants.

 The founder's earlier company had already consumed roughly $170 million before collapsing. 

 A $33 million (pre-crash price) token unlock was seventeen days out. 

 The token cratered by about 90% , the bridges were halted , and the BSC contract still belongs to the attacker. 

 When a protocol's entire value proposition is trust, what exactly does it mean when the trust runs out? 

 Credit: Humanity Protocol , bloomingbit , The Defiant , QuillAudits , ZachXBT , banteg , PeckShield , Protos , decrypt , CoinDesk , Specter , Terence Kwok , Beosin , SlowMist , Quantstamp , Crypto News , Ogle , CoinTelegraph , DLNews , HTX , H Foundation , Tokenomist 
 Specter flagged it first. 

 Specter highlighted that wallets that had interacted with Humanity Protocol were being drained , 17 of them, at that point.

 Losses were already past $5 million and climbing at the time.

 The root cause was still unknown, but the pattern was hard to misread - something connected to the protocol itself had been compromised, and the money was moving fast. Theft addresses were already hitting the timeline. 

 An hour and a half later, Specter was back with an update. Losses had crossed $20 million. $9 million had already been swapped into ETH. Another $9.9 million in $H was sitting in attacker-controlled wallets, not yet converted, as if whoever was behind this was in no particular hurry. $H was already down 87% from the sell pressure alone.

 Terence Kwok roughly half an hour later , the statement was measured, minimal, and notably vague about what had actually happened: "We've detected a security incident involving the compromise of private keys belonging to a member of the Humanity Foundation. As a precaution, please do not interact with the bridge or any liquidity pools until we confirm it's safe." 

 A private key. One member. That framing would not survive the night.

 A fuller official statement followed from the Humanity account , warning users about scammers and impersonators, confirming the team was working with security experts and exchange partners, and drawing a hard line: Official updates would only come from the protocol account or from Kwok directly.

 Standard incident playbook. Nothing in either post told holders how bad it was, or how much worse it was about to get.

 Beosin was already on the case. By early evening they had traced approximately $16.2 million in $H swapped into ETH and consolidated at a single address. The picture it painted was not one of chaos. It was methodical.

 Then PeckShield flagged something that changed the shape of the story entirely. An attacker-controlled address on BNB Chain had minted 100 million $H directly from the null address.

 New tokens, printed from nothing through a malicious unlimited mint function the attacker had just deployed.

 A second batch of 100 million followed. Then another. Then more, multiple tranches across BSC before the protocol could respond .

 This was no longer a wallet drain. Someone had rewritten the rules of the token mid-game.

 ZachXBT arrived shortly after, and he did not arrive quietly : "The 'incident' seems possibly staged. I am not buying the teams story, it's a convenient way for the active MM to have exited."

 Twenty minutes later he escalated : "You choose to crime pump your token for weeks with zero fundamentals and think CT will blindly trust your story? Disclose your active MM agreements with the HK entity first…"

 Two things in that later post were notable.

 First, the accusation wasn't just about the hack , it was about the weeks before it. The up only chart behavior , that ZachXBT himself described as a token being "crime pumped for weeks with zero fundamentals." 

 Second, the demand : Name the Hong Kong market maker. Publicly. The team never did.

 By later that night, banteg surfaced the on-chain message the attacker had sent to Chris Blec - and whatever ambiguity remained about the state of Humanity Protocol's internal security evaporated in a single sentence: "i was stressing out about needing to social engineer four different devs across three different timezones. then you drop a revelation that it's actually just one guy with six signer keys in his metamask. thank you king." 

 Not a sophisticated operation that cracked a hardened target, a relief operation.

 The attacker had been prepared for a difficult job and discovered, mid-execution, that someone had already done it for them. 

 When the attacker finds your security setup funnier than you do, how do you explain that to the people who trusted you with their money? 

## One Bad Laptop

 The official explanation arrived on June 9 . 

 A developer's laptop had been infected with malware . The attacker obtained full root access to the machine. 

 Seven production private keys had been backed up to that device approximately one year earlier , during mainnet setup.

 No smart contract was exploited. No protocol logic was broken. Every action the attacker took was technically legitimate, they were simply using credentials they had no right to hold. 

 Seven keys, one machine, backed up there a year ago and never rotated out. No red flags here, right?

 The Incident Update framed this as an operational security failure rather than an architectural one. 

 That framing is technically accurate and almost entirely beside the point. The architecture was built on an assumption - that the keys would stay separate, stay safe, stay distributed. When that assumption failed, there was nothing underneath it. 

 No timelock on the ProxyAdmin , no circuit breaker, no monitoring window between the moment the signing threshold was crossed and the moment the upgrade executed.

 The design required the keys to be secure. They weren't. Everything that followed was automatic.

 Terence Kwok told CoinTelegraph what happened in more precise terms : "What we believe happened was some of the keys were accidentally backed up to a compromised device."

 He added that for certain contracts , multisig keys were "set up in one place and then dispersed," leaving some backed up on a compromised device. 

 Kwok also confirmed that the multisig controls were spread across just four individuals , meaning in a six-signer Safe, some people held more than one key. 

 A multisig with six signers provides meaningful protection only if those signers are genuinely independent, different people, different machines, different attack surfaces.

 Three of the six Ethereum Safe owner keys and three of the five BSC Safe owner keys were all recoverable from a single endpoint.

 The threshold required to execute was three. The attacker had three. The multisig was theater.

 On June 11th, Quantstamp published their preliminary investigation findings , and named the person whose device was at the center of it all. 

 Chong Yee Wai, a director of Humanity Protocol , received a spear-phishing email on June 5, 2026 at 02:00 UTC. 

 The email impersonated Korean exchange Bithumb with a malicious attachment , Bithumb_Circulating_Supply_Lockup_Schedule.zip, hosted on an attacker-controlled domain.

 Believing it to be genuine , Chong downloaded it, filled out the spreadsheet, and cc'd his colleague Terence Kwok, who independently received the same phishing email at a different unique URL, a standard technique to track which victim was infected.

 The attachment delivered hncagent.exe , a first-stage loader signed with a South Korean Hancom certificate. 

 Quantstamp noted the pattern was "characteristic of DPRK intrusions." 

 By June 7, the attacker had remote-desktop access to Chong's Windows machine . Neither Sophos nor Windows Defender detected any of it. 

 From there, the attacker copied Chong's MetaMask Chrome extension and its encryption key , the same MetaMask the banteg message had already exposed held six signer keys.

 The next day, the on-chain attack was executed.

 QuillAudits identified the compounding failure cleanly: The ProxyAdmin had no timelock. 

 In a system where the ProxyAdmin controls the upgrade path for both the bridge contract and the token logic, whoever holds that admin key holds everything. 

 A 24-hour delay, combined with event monitoring on the AdminChanged function, would have given the team a window to respond before a single token moved.

 That window did not exist. The moment the attacker crossed the Safe threshold, the outcome was already decided.

 Banteg noted something else that the incident report passed over quietly . While the BSC Safe keys were rotated in the hours after the exploit became public, the Ethereum wallet remained compromised for at least fourteen hours. 

 The team had begun responding on one chain while the attacker retained live access on the other. That gap, whether the result of coordination failures, incomplete understanding of the breach, or something harder to explain, is not a small detail. 

 The attack unfolded across three distinct vectors. 

 First, the compromised admin hot wallet was used to transfer 6,045,060 $H directly to an aggregation wallet on Ethereum , no contract interaction required, just a key and a transfer.

 Second, three of the six stolen ETH Safe owner keys were assembled offline to cross the signing threshold, transfer ProxyAdmin ownership, upgrade the bridge to a malicious implementation, and drain 141,182,632 $H in a single transaction .

 Third, the same playbook executed on BSC - three of five keys, same ProxyAdmin seizure, malicious implementation deployed, unlimited mint function activated. 

 SlowMist's classification was precise: Private Key Leakage.

 No audit would have caught this. No bug bounty program covers it. The contracts were not broken. The people responsible for the keys were. 

 When the architecture's only real defense is "the keys won't leak", and they do, what was the architecture actually defending? 

## Print, Drain, and Exit

 On June 8, someone used a key they had no right to hold and moved 6,045,060 $H from the compromised admin hot wallet to an attacker-controlled wallet . 

 No contract interaction. No multisig ceremony. Just a stolen key and a transfer. $H was trading at approximately $0.62 at the time. 

 Hot Wallet Drain: 
 0x94a4b4a37439ad5c01a84b504c7f58eb5c2ab560352f147f78e62802bf4ee015 

 That was the opening move. What followed was not improvisation.

 Using three of the six Ethereum Safe owner keys, enough to cross the signing threshold, the attacker assembled an offline transaction and transferred ProxyAdmin ownership to a wallet they controlled.

 They then upgraded the bridge contract to a malicious implementation and swept 141,182,632 $H in a single transaction , raining the entire bridge contract in a single transaction.

 ETH Bridge Drain: 0xa665998ca9a2fcfe66d687647edede62c7acd554c7d35ea13c93788b8a129e5b 

 On BSC, the same playbook was executed, with three of the five stolen Safe keys. The ProxyAdmin was seized, the malicious implementation was deployed, and the unlimited mint function was activated.

 Then the attacker called mint() three times , 100 million H per call. 

 BSC Mint 1: 
 0x5a8f82f1064a7846ab3eb77bd1d36ec52dfd773c3957ad0aeea28da95fe9c5fb 

 BSC Mint 2: 
 0x56a150859637e453679d833bbff0d1bdfe9b8a288ca1e7190b678940dd7208f3 

 BSC Mint 3: 
 0x813b340ce6fac66764a182c94d1d3c8d1aec3686e434bb19c82d12c98867e746 

 Three hundred million tokens printed from nothing, the figure confirmed by Humanity Protocol's own incident report .

 QuillAudits documented a far larger picture : An additional 1,000,000,000 H minted in a single transaction, plus two further 100,000,000 H mints beyond the three the team confirmed, bringing the total BSC minting activity documented on-chain to approximately 1,500,000,000 H.

 BSC Mint - 1,000,000,000 H (undisclosed): 0x50662e5ff99298e0c8e5bb23f532be4e92d764ec507de46cb90b96a3f2831aab 

 BSC Mint - 100,000,000 H (undisclosed): 0x3d52ab7994f483498ab37f3c54a3850cba5cd9b3c2ff5011c629c925da5b5607 

 BSC Mint - 100,000,000 H (undisclosed): 0x12816ceb6c2a28ff0e926f1ede112487a224d4be84b9b01373b4971e2bb38b57 

 The team has never addressed the discrepancy in any official communication.

 Humanity Protocol's post-mortem acknowledged 447,227 million $H across the three attack vectors - 6,045,060 H from the hot wallet drain, 141,182,632 H from the ETH bridge sweep, and 300,000,000 H from the three BSC mints the team confirmed.

 QuillAudits documented substantially more on-chain , approximately 1,641,182,632 $H when including all BSC mint transactions the team has never accounted for.

 What the attacker actually walked away with was $36 million , the proceeds of dumping stolen and minted H tokens into their own selling pressure across decentralized exchanges only, never touching a centralized platform.

 Arkham Intelligence mapped the full theft cluster under the “Humanity Protocol Exploiter” entity: 

 Humanity Protocol Exploiter on Arkham (12 addresses) 

 Beosin tracked one confirmed consolidation point where $16.2 million $H have been swapped into ETH and consolidated and held by one address: 

 0x9e995952eF7665B243eeEF0693acD7FEd7150504 

 Since then, the funds were transferred to these following addresses: 

 0xf3599f3C7dD37FF42B043A2945E90E98B4Fc9734 
 0x365e14eDFC2D4F582c814C40162f3846aCbce672 

 As of publication, the consolidation wallet holds approximately 21.7 million $H .

 Humanity Protocol launched a live tracker of the exploiter’s addresses and downstream transfers at transparency.humanity.org and offered a $1 million USDT bounty for information leading to recovery .

 The attacker has not responded.

 Twelve addresses, a structured exit, $36.4 million through Uniswap.

 The plan was executed - but with law enforcement engaged, exchanges flagged, and the on-chain trail mapped for anyone to follow, the bigger question isn't how they did it. 

 It's who did it, and whether they'll ever answer for it? 

## Still Their Keys

 ZachXBT updated his position on June 8th. 

 After further analysis of the laundering trail , he concluded the market maker activity and the private key compromise appeared to be independent of one another. 

 ZachXBT : "Kind of funny if the team was pumping the token for weeks only to have gotten rekt shortly before the upcoming unlock later this month."

 That walk-back was not an exoneration. The demand to disclose active market maker agreements with a Hong Kong entity remains publicly unanswered.

 The team has never addressed it.

 Weeks before the hack , the Humanity Foundation had already sent revised vesting terms to over 100 early investors, a binary choice between a 70% haircut for immediate liquidity on June 25, or an extension of the cliff to September 2026 with quarterly distribution over three years . 

 One early backer, Ogle, wrote on Twitter : "When a founding team treats its early backers with complete hostility as this one has, and disregards signed agreements, it's hard not to wonder what's actually going on behind the scenes of the company." 

 Dr. Hakan Ünal, senior security operations lead at Cyvers, told CoinTelegraph that the on-chain pattern can look similar whether an incident is a genuine compromise or a staged event, because the attacker holds legitimate admin rights in both cases.

 “ What distinguishes them”, Dr. Ünal said, is the surrounding behavior : "A genuine compromise usually shows speed and improvisation: funds rushed to fresh wallets, swaps at bad prices, mixer use, and no insider timing. Right now the evidence is mixed, which is why the question is open."

 Allium Labs research lead Elton Shehdula went further. His forensic analysis of the on-chain pattern concluded it was consistent with a potentially planned and coordinated operation rather than a lone opportunist.

 Attacker wallets were funded from an exchange and a mixer weeks in advance . The minting authority was warmed up days before the attack. The dump executed across two chains simultaneously. 

 Shehdula described the level of setup as consistent with either an insider or an outside actor who had quietly held the compromised key for some time. 

 PeckShield published the most detailed on-chain forensics of the pre-attack period on Telegram.

 Their analysis traced a major $H holder who sent 20 million $H (~$5.16M) to address 0x686d1d7B on May 28, just ten days before the hack.

 The sending address was later drained to 0xD1ea823D , now labeled Humanity Protocol Exploiter 5 on Etherscan.

 Major $H Holder: 
 0x91844A3C6BDA5B1c1f663e2280F99896efe06F42 

 Destination Address: 
 0x686d1d7B04e453dcdA68e6C003271ce20E01BE37 

 Later drained to (Humanity Protocol Exploiter 5): 0xD1ea823D421E0c829ee11F772AF487fd352678EA 

 From there, 56.7 million $H (~$15M) moved to two BitGo deposit addresses on May 29th.

 2 BitGo Deposit Addresses: 

 0x6E6a9fCC3A26aB1F85BF87fb8c544Af42699ce5b

 0x0E0e9fE6B97c9d4EaF040A7365c78F431064D1E0 

 During Rekt News on-chain analysis, a further ~5.9 million $H was found to have moved into one of these same BitGo deposit addresses on June 8, the day of the exploit. 

 June 8 transfer into BitGo Deposit Address 2: 0xa8dc8dbf6dee00d615a44d643dadef7a5d403c4525535abfe594401732bb6acb 

 A separate address received $6 million USDT from FalconX on May 30 and forwarded it to OKX.

 FalconX Transfer 1 (4 million USDT): 0xbe45706c5fd2753cea76de59c85878b021a89b4d476c66846f4c227e86ef3de7 

 FalconX Transfer 2 (1,999,990 USDT): 0x20072681946fc27edecb76bda885b2a9c255c0dd92e81e00dbbb34a6645384a5 

 FalconX Transfer 3 (9 USDT): 0xf5275113711d55d131bd63c6117ed42ff5934b6675d319d3300a7a15be5b6f3b 

 Address that sent $6 million USDT to OKX Deposit Address: 

 0x3dB75DF4104255528674f798DeC42Ff3977740bd 

 PeckShield also traced a second large holder , who on May 28 sent a record 72 million $H (~$12M) to a wallet linked to a supposed market maker financier.

 Large $H holder (related to Exploiter 1): 

 0xbaAb7211438F33bE0344d57978C7571f2d797ab2 

 Wallet that transferred large assets for the supposed market maker: 
 0x943839Ff3D418C1435d4458e533FD90696D65238 

 Peckshield mentioned that the activity of these addresses resembled that of a market maker operating across several centralized exchanges. 

 PeckShield's conclusion was unambiguous : "The protocol developer's keys, the market maker's financier keys, and the market maker's wallet keys can't all be on the same computer. Therefore, I'm certain this wasn't an attack. I'm certain this was a staged performance, which, at its core, is nothing less than a Rug Pull."

 ZachXBT's laundering analysis arrived at a different conclusion , that the market maker activity and the hack were independent.

 But both investigators agreed on one thing: Something unusual was happening with Humanity Protocol's token before the exploit began.

 Then there is the question of the project itself.

 Kwok confirmed to DLNews that of the 9 million Human IDs registered on the network , just under one million had completed biometric verification, meaning up to 88% of claimed users may have been bots. 

 For a protocol whose entire value proposition was proving you were a real human, that number is difficult to reconcile. 

 The BSC token contract remains under attacker control. The ProxyAdmin has not been recovered.

 Whoever executed this still holds the ability to mint $H on BSC at will .

 Meanwhile, the core team behind Humanity is already involved with a new project called "Everything," which raised $6.9 million in seed funding in January 2026 , led by Humanity Investments, Humanity's own venture capital arm, with participation from Animoca Brands and Hex Trust.

 Community members have speculated that the hack may have been a deliberate scheme to abandon $H while shifting focus to the new venture. 

 That has not been established. But the timing is its own kind of answer. 

 The team has not addressed ZachXBT's market maker allegations. 

 The bridges remain halted. 

 An official recovery portal is now live at humanity-recovery.com . 

 Pre-incident holders can exchange legacy H for repegged H at a 1:1.048 ratio , with a window that closes June 22, 2026.

 The old H token has been sunsetted across Ethereum, BSC, and Humanity Mainnet. A new audited ERC-20 has been deployed on Ethereum, with a 1:1 airdrop to holders whose balances were captured in a snapshot taken at June 8, 17:25:35 UTC, roughly seven minutes before the first transaction of the attack.

 New H Token Contract: 

 0xE76c5b78f93909d34404E9eb4C1f19e7582a5dE1 

 For complex cases that cannot be resolved by the automated airdrop, a dedicated H Compensation Fund and claims portal has been established at claim.humanity.org . 

 Claimants are required to complete identity verification before any compensation can be processed - because the exploit has been linked to DPRK-affiliated actors, the team says, AML compliance is required. 

 A protocol built to verify who you are is now asking its exploited users to verify who they are before they can be made whole.

 The June 25 unlock , 266.5 million $H across six allocations including the foundation treasury and a strategic reserve, visible on Tokenomist for any trading desk to see, is still scheduled, at a token price now a fraction of what it was when investors were forced to choose between a haircut and an extension.

 A protocol built to prove you are who you say you are, and it still can't tell you who did this. 

 If the Humanity Protocol can't answer that question, what exactly are holders being asked to trust? 

 Humanity Protocol raised $50 million to build the trust layer of the internet , and collapsed in a single night because seven private keys lived on one laptop , later attributed to a spear-phishing attack that Quantstamp identified as bearing the hallmarks of a DPRK intrusion . 

 The founder had already watched $170 million disappear once before. 

 The foundation had Mario Nawfal , one of crypto's most prolific hype merchants, a s a founding director .

 Early investors had been forced into a binary choice between a haircut and an extension weeks before the token lost most of its value .

 A multisig with six signers turned out to be one laptop. A proof-of-humanity protocol with 9 million registered identities may have been mostly bots. 

 A trust layer that couldn't secure its own keys is now asking its community to trust it while the BSC contract remains in the hands of whoever took it. 

 When Quantstamp published their preliminary investigation findings, Specter, the first person to flag the exploit, called it the shortest post mortem to read - no timestamp, no details, just repeating what we already know. 

 The irony was always the product.

 Humanity Protocol sold the world a way to prove you are who you say you are.

 We now know whose device was compromised, which is rare for a private key leak.

 What we still don't know is whether anyone will answer for it. 

 In a space where the lesson is learned after every exploit and forgotten before the next one, what will it take for a protocol to actually be what it claims to be? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

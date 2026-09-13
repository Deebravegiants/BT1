# [H] 1Inch exploit: Five million dollars vanished when 1inch's deprecated code returned from the dead to haunt its creators

## Summary
Severity: High
Target: 1Inch
Loss: $5,000,000
Published: 3/5/2025
Source: https://rekt.news/1inch-rekt
Type: rekt-postmortem

## Details
## 1Inch - Rekt

 Thursday, March 13, 2025 1Inch - Rekt 

 read this article also in : 

 Five million dollars vanished when 1inch's deprecated code returned from the dead to haunt its creators. 

 A few market makers, or resolvers, watched helplessly as a calldata corruption vulnerability transformed their contracts into ATMs for a crafty attacker who needed nothing more than basic arithmetic and an integer overflow. 

 The _settleOrder function, supposed to be long retired, was a relic from 1inch's earlier architecture where vulnerabilities could silently thrive - a perfect attack vector hiding in plain sight.

 Nine audit teams missed it. Two years passed without incident.

 Then one hacker with a calculator and a dream discovered that setting an interaction length to negative 512 could underflow memory pointers and redirect suffix data - transforming a simple integer trick into positive millions.

 The exploit's elegance was brutal in its simplicity - cracking a nine-times-audited vault with nothing but a negative number and the audacity to try it.

 Mid-heist, our digital bank robber took a moment to slide a note across the counter: "Can I have bounty?"

 Because in crypto's backwards universe, robbers expect tip jars at the scenes of their crimes. 

 Still think those security guarantees are worth the PDFs they're printed on? 

 Credit: 1Inch , Slow Mist , Decurity , shoucccc 
 On March 6th, 1inch announced the discovery of a vulnerability in their obsolete Fusion v1 resolver contracts, correctly stating that 'No end-user funds were at risk.' But their message didn't mention that about $5 million had already been stolen from resolvers' funds. 

 Just another day patching legacy code.

 But something critical was missing from their initial postmortem - about $5 million in actual stolen funds.

 The full extent of the theft didn't come to light until security firm SlowMist conducted their own investigation the next day. They uncovered what 1inch conveniently missed : 2.4 million USDC and 1,276 WETH already gone - digital smoke where money used to be.

 The attacker's wallet funded through Tornado Cash began its methodical assault on what should have been battle-tested contracts. 

 Attacker Address (Exploit Deployer): 

 0xa7264a43a57ca17012148c46adbc15a5f951766e 

 Attack Contract: 
 0x019bfc71d43c3492926d4a9a6c781f36706970c9 

 Funds Receiver: 
 0xbbb587e59251d219a7a05ce989ec1969c01522c0 

 Victim addresses: 

 TrustedVolumes: 
 0xb02f39e382c90160eb816de5e0e428ac771d77b5 

 1inch Settlement V1: 

 0xa88800cd213da5ae406ce248380802bd53b47647 

 The attack unfolded through a series of meticulously crafted transactions: 

 0x04975648e0db631b0620759ca934861830472678dae82b4bed493f1e1e3ed03a 

 0xb5c94efa0c8fd8f5c8cc2826e374a99620b01061d395b59b8f45dddc9fce1c60 

 0xb16bbf03d324b66685c94d62dbe31c739ee23c114b3915d169c74cd7c98eec8c 

 0x3947e5a4d98104e313e08ee321673e1183db3d6ff8b7207f3eabb36f71436c1d 

 0x9ce5187c7160f531189e4765f21af5975dc2a62d961fb61ae09866d082918256 

 0xb0688eb1f46c28f36d7397366146fced23d3f8da7e08b760a5f612ce134ee9d2 

 0x62734ce80311e64630a009dd101a967ea0a9c012fabbfce8eac90f0f4ca090d6 

 Regular users scrolled through their untouched balances while market makers like TrustedVolumes watched their funds vanish faster than exchange executives during a bear market.

 Forget million-dollar exploits and state-of-the-art hacking tools. Our attacker brought a calculator to a gunfight - and won. 

 Each transaction followed the same playbook: 

- 
 Create a normal order swapping pennies for millions.

- 
 Pad it with null-bytes.

- 
 Set interactionLength to "-512" (0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe00).

- 
 Add a fake suffix structure as an interaction.

- 
 Watch as memory pointers underflow and redirect control to TrustedVolumes.

 Like clockwork, resolver after resolver fell as the 0x1944799f function signature ("resolveOrders") became the skeleton key to everyone's vaults.

 The attack climaxed with a series of transactions in rapid succession: 

 0xc69b4c8029c70ae468e92af31120ac6b01bb89c6e35d34818413e9942aedebb6 

 0xefcb740bf9ec17ed99839ffcc05393fae5ec2d44149aee91ba119f48bc20a1ef 

 0x74bc4d5dc7f8da468788da6087bb9f73465966ab5b8cf9cf1053d98e78a9bf96 

 By 5:54 PM UTC, the damage was done.

 Want the magic number that turned millions of dollars into thin air? 512.

 Or in hexadecimal: 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe00—for those who prefer their nightmares in base 16.

 With that single value, the attacker weaponized integer underflow—sending memory pointers spiraling backward, hijacking resolver addresses, and redirecting function calls like a traffic cop on bath salts. 

 The mechanics would make even the most jaded CTF players slow-clap in appreciation. 

 Create a normal-looking order to swap a few wei for millions. Pad with zeros. Use the negative interactionLength to corrupt calldata and hijack the resolver address.

 Resolver security checks? Bypassed.

 Protocol safeguards? Sidestepped.

 Audit guarantees? Worthless.

 All with a four-byte integer trick that would barely earn partial credit in a freshman coding class. 

 When the most dangerous security threats come from elementary school math, what exactly are we paying those nine audit teams to find? Advanced calculus? 

## The Aftermath

 In DeFi's twisted universe, stealing money is just the beginning of the negotiation. 

 Our hacker, fresh off a multimillion-dollar heist, sent an on-chain olive branch : "Can I have bounty?" - the DeFi equivalent of asking for a tip after cracking the vault. 

 What followed wasn't the expected "go to hell" but instead a surprising twist: TrustedVolumes slid into the thief's on-chain DMs to start haggling.

 Five hours later, at 11:55 PM UTC, negotiations concluded with blockchain's most awkward handshake.

 By midnight, the attacker started trickling funds back to TrustedVolumes, keeping just enough for what Crypto Twitter would generously call a "white hat fee" - because nothing says "ethical hacker" like stealing millions and returning most of it.

 By 4:12 AM on March 6th, most funds were returned, with the attacker pocketing roughly $450,000 - a 10% "finders fee" that makes traditional robbery seem inefficient by comparison.

 Funds Returned Transaction 1 ($2.4M USDC): 
 0x99ff2067bfa6f5e30afcefc45477cb5bb661d85890ece002a4a0ce348a3c6e7a 

 Funds Returned Transaction 2 (1076 ETH - $2.09M): 
 0xbe270b797de02c382df8c569813837fc0a6bb97809fd8a512b50c87c750bc367 

 The fun part? The hacker's fumble created a secondary comedy of errors.

 In the chaos of moving stolen funds, they accidentally sent half their haul to the 1inch settlement contract itself - essentially dropping millions into a public swimming pool.

 This triggered a mad dash as shoucccc and others raced to snatch the exposed funds:

 "The funny thing is the hacker incorrectly transferred half of the stolen funds to the 1inch settlement contract, making the funds available for everyone to grab, and he spent quite sometime to get funds back. We were trying to compete but the hacker got it first unfortunately."

 A multi-million dollar game of finders-keepers, with the original thief scrambling to recover their own stolen goods before someone else stole them again. Only in crypto. 

 2 days after the hack, security firm Decurity released one of the most comprehensive and lightning-fast postmortem analyses in recent history. 

 Researcher Omar Ganiev's breakdown was so thorough and timely it made some security firms look like they're still using carrier pigeons.

 Ganiev distilled the soul-crushing reality: despite nine audit teams and multiple reviews , the fatal flaw was nothing more than a glorified buffer overflow - a bug too basic for auditors to catch, yet sitting in plain sight for years, waiting for its moment.

 The bug slithered into existence in November 2022 when 1inch traded Solidity for Yul - a language switch that birthed a memory overflow monster that nine audit teams couldn't spot with a telescope. 

 This wasn't just a subtle bug - it was yet another red flag in institutional blindness and security theater as highlighted in Decurity's remarkably candid postmortem that exposed their own role in the oversight. 

 Audit round one kicked off in October 2022 on perfectly clean code.

 Then November came, and 1inch switched from Solidity to Yul - like swapping your family sedan for a Formula 1 car without checking if anyone knew how to drive it.

 By December, multiple firms were pawing through the refactored code, but conveniently the _settleOrder function fell into that magical "not in scope" dimension where vulnerabilities go to thrive.

 March 2023 brought a glimmer of hope when Decurity actually spotted the integer overflow risk. 

 But in classic DeFi fashion, 24 hours later a new implementation appeared, and everyone forgot the old infected code was already loose in the wild - like noticing your lab sample has Ebola but forgetting you already mailed copies to everyone on your Christmas list. 

 For over two years, the bug lounged in production code, sipping cocktails, undisturbed by the parade of security professionals who couldn't see what was hiding in plain sight.

 No one exploited it not because it was cleverly concealed, but because everyone was too busy admiring the emperor's new audit reports to notice he was actually naked.

 The real lesson? A vulnerability doesn't expire with age. It just waits for someone who bothers to actually look.

 The final tally: TrustedVolumes got most of their $4.5M back minus the 10% 'bounty' the attacker kept ($450K). 

 The 1inch protocol itself slipped away technically unharmed - unless you count the reputational equivalent of hosting a $5 million bank robbery on your property using keys you should have changed years ago.

 For their part, 1inch announced a bug bounty program faster than you can say "stable door, missing horse" and urged resolvers to "audit and update their contracts immediately " - advice that might have been more useful before their resolver partners got sliced.

 Audits aren't magical protection spells - they're expensive snapshots by people who rarely verify what actually gets deployed after cashing their checks.

 The real kicker? We're still learning the same lesson, sometimes the deadliest weapon isn't a zero-day exploit or quantum computing breakthrough - it's a negative number and the audacity to use it. 

 When your multi-billion dollar industry's security model can be unraveled by arithmetic that wouldn't stump a fifth-grader, who's really being naive—the hacker who tried it, or the protocol that never thought they would? 

 Multiple audits, multiple firms, two years of smug security guarantees - and still rekt by fourth-grade arithmetic. 

 Welcome to DeFi's most expensive security theater, where the tickets cost millions and the actors don't know their lines. 

 1inch's bugs sat in broad daylight like financial IEDs, patiently waiting for someone brave enough to attempt the most dangerous act in crypto: adding negative numbers.

 Smart contracts don't decay, but human attention does.

 What nine firms stamped as "secure" in 2023 transformed into a hacker's personal ATM in 2025 - all because no one bothered to check whether yesterday's "safe" code might nuke tomorrow's systems when they meet.

 The uncomfortable truth? Projects brandish audit reports like medieval talismans against evil spirits, while your most thorough auditors remain the hackers who examine your code with dollar signs in their eyes and empty wallets in their hands. 

 The only question is whether you'll pay them before or after they've emptied your treasury.

 1inch only found religion about security after $5 million had already walked out the door - proving once again that in DeFi, security consciousness arrives exactly one exploit too late.

 In a rare display of accountability almost as unusual as a solvent crypto exchange, Decurity confessed to its own role in this circus - admitting they actually spotted the bug in March 2023 but lost track of it when the code was refactored, like a security guard who notices the bank vault is unlocked but gets distracted by a doughnut. 

 Will an industry worth billions ever realize that paying hackers after they rob you isn't a security strategy, it's Stockholm Syndrome with a blockchain address? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

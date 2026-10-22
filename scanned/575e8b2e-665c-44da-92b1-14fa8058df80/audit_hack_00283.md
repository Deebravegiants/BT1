# [C] UXLink exploit: One delegateCall was all it took to turn UXLINK's treasury into someone else's $41 million withdrawal slip - though tracking the full damage across mu

## Summary
Severity: Critical
Target: UXLink
Loss: $41,000,000
Published: 9/22/2025
Source: https://rekt.news/uxlink-rekt
Type: rekt-postmortem

## Details
## UXLink - Rekt

 Thursday, September 25, 2025 UXLink - Admin Privileges - Rekt 

 read this article also in : 

 One delegateCall was all it took to turn UXLINK's treasury into someone else's $41 million withdrawal slip - though tracking the full damage across multiple chains continues to reveal new depths to this heist. 

 Someone with multisig access decided the vault was theirs for the taking, using delegateCall to remove admin roles and install themselves as the new owner. 

 What followed was a textbook example of why emergency functions make excellent getaway vehicles - over $4 million in stablecoins, 3.7 WBTC, and 25 ETH were initially reported as stolen across chains faster than you could say "social network."

 But UXLINK's Web3 social platform got a lesson in cosmic justice when their attacker became the victim.

 Minutes after minting trillions of unauthorized tokens, the exploiter fell victim to their own medicine - a phishing scam that drained 542 million UXLINK tokens into addresses linked to Inferno Drainer. 

 When your multisig becomes a single point of failure, who's really holding the keys to your kingdom? 

 Credit: Cyvers , Mannie , how2onchain , Vladimir S. , UXLink , ExVul , Blockscope , Peckshield , Hacken , CoinMarketCap , Cos 
 UXLINK's silence was deafening while their treasury bled dry across multiple blockchains. 

 How2OnChain spotted the bleeding first on September 22nd - $5.3 million in UXLINK tokens moving fast, triggering immediate dumps.

 Cyvers caught more of the scope thirty-five minutes later : as they reported $11.3 million vanishing as someone used delegateCall to kick out the old admins and crown themselves king of the vault.

 Vladimir S. started picking through the wreckage , tracing swaps and following wallet breadcrumbs while UXLINK played dead. 

 92 minutes. That's how long it took for UXLINK to admit they'd been cleaned out , finally posting the corporate equivalent of "oops, someone robbed us."

 "We have identified a security breach involving our multi-signature wallet, resulting in a significant amount of cryptocurrency being illicitly transferred to both CEXs and DEXs."

 But this wasn't your typical flash loan exploit or price manipulation masterpiece - this was administrative betrayal wrapped in smart contract jargon. 

 When your emergency response time is longer than a Netflix episode, what exactly are you protecting users from? 

## The Admin Coup

 UXLINK's multisig wasn't hacked - it was hijacked. 

 No complex DeFi jujitsu. Someone with admin access just decided the treasury belonged to them now. 

 The delegateCall came first - blockchain's version of changing all the locks while everyone's asleep.

 One function call to boot the old admins, another to install themselves as the new boss via addOwnerWithThreshold .

 The contract didn't know the difference between legitimate governance and a hostile takeover - it just followed orders from whoever held the admin keys.

 This was administrative betrayal wrapped in smart contract jargon. 

 When your security model assumes the people with access won't rob you blind, what happens when they do exactly that? 

## The Ugly Autopsy

 The digital footprints tell an ugly story. 

 Starting with this attacker’s address taking complete control of UXLINK's treasury: 

 0x2EF43c1D0c88C071d242B6c2D0430e1751607B87 

 Then ~$18 million walked out the door across several chains - the seed money for what would become a much larger operation.

 Blockscope security researcher Gangsterhome helped provide the forensics breakdown to Rekt News.

 The initial attack transactions are as follows… 

 On Ethereum Mainnet: 

 25.27 ETH ($105k): 

 0x618e914f8c0afccaaf9be2d502730aa9c89f6cb0cc63aa6e700ef7e1d659b093 

 $2.68M USDT: 

 0x725a490ee5cd49209b08cf5b7e7513656098d1c174acdf006707b2d5589654bd 

 $1.3M USDT: 

 0x30c72951bce511d4b189844ef750b69fe07d9b78817167ae3ec28628860c2989 

 3.7 wBTC ($420k): 

 0x00de60732cb5ca53ad2ac0a2babdc63f94239645309ee097dddb7ed350a1f7e7 

 $1.45M USDT: 

 0x278bfd667d9d3e55a33f9255457b3cd4522b96294de4fdc8b79583835491e63c 

 $500K USDC: 
 0xf8dce9dfe0ef189b5fe7ad4cded7ef1e4bfffd6955dc1fcd8f3c2b7259afc650 

 $123K USDT: 

 0xc609ec7be6274c513fadfb6a95e009b395fd3c4805e81f4896e7ebd89d38dddd 

 Total stolen on Ethereum through the initial theft address: $6.578 Million.

 The stolen funds from above were sent here: 

 0x6385eb73faE34bF90Ed4c3d4c8aFBC957FF4121C 

 Then some of the funds were swapped and transferred here: 

 0xaC77B44A5F3acC54E3844A609fffd64F182ef931 

 Initial theft address you say? Because the damage is worse than initially reported.

 Another address did almost twice the damage on Ethereum Mainnet around the same time in several transactions: 

 0xb819e6ae5a6668bb0ce02d64d130deca9ff83691 

 What was stolen on Eth Mainnet in Round 2: 

 $5.382 million DAI
$1.377 million USDT
4.009 million USDC
4.7327032 WBTC ($538k)

 Total from this theft: $11.3 Million

 View the 2nd exploit transaction tracing on Ethereum on Metasleuth here: 

 UXLink 2nd Ethereum Exploit 

 Total theft on Ethereum: $17.885 Million

 Meanwhile on BSC, smaller amounts were stolen. 

 BSC theft totals: 
19.5k KiloEx - $91
70k SOLV - $2,902
$23,943 Binance Peg USDC

 BSC total: ~$26,936

 View BSC transaction tracing on Metasleuth here: 
 UXLink Exploit on BSC 

 Combined initial theft: Almost $18 million across Ethereum and BSC.

 This was just the beginning, as stealing treasury funds was just the appetizer. 

 The ~$18M treasury drain was just the down payment - the real payday came from infinite mints and multi-chain laundering. 

 The real show started when the attacker discovered they could print money.

 Mint transactions began flowing like water.

 UXLINK broke the news themselves : "We have identified an unauthorized minting of UXLINK tokens today by a malicious actor."

 The first 1 billion UXLINK tokens were minted in this transaction: 

 0x35edac40767f65d4d1382f0f55cda2f4db321313e16fe059079f0113f9cb5696 

 PeckShield flagged the UXLink token with "DO NOT TRADE" warnings.

 Then came the second billion in this mint: 

 0x2466caf408248d1b6fc6fd9d7ec8eb8d8e70cab52dacff1f94b056c10f253bc2 

 PeckShield flagged the second mint too , while Hacken piled on with estimates that the attacker created almost 10 trillion tokens total , with continued minting tracked throughout the day. 

 By the time all the security firms were sounding alarms, the attacker had turned UXLINK's carefully planned tokenomics into hyperinflationary chaos. 

 Blockscope's forensics applied a lot of elbow grease and revealed the scope : roughly 6,700 ETH (~$26.8 million) moved from Arbitrum to Ethereum through sophisticated cross-chain operations using Across Protocol and Defiway .

 The attacker used multiple unlabeled wallets to systematically mint billions of UXLINK tokens on Arbitrum.

 Swap them for ETH through DEXs like CoW Protocol. 

 Bridge substantial ETH amounts to Ethereum Mainnet.

 The money trail leads to ten addresses where the exploiter's funds currently sit, maybe waiting for the next move. 

 Addresses involved in holding exploiter funds (as tracked by Blockscope): 

 0x64ab9377a2b3bbb61dd79f8997e7f8c1cc1a4de8 

 0x7277c705b5b1963b602cb4e3ab8e188d925bed00 

 0xf35dde49a1bbe7a8883a8f35d48fb33c20a69b39 

 0x7e1f34418e2da204a8eabdb29eddf7c09a494a3f 

 0x5210bfdf0cfe6471322d597d16cf440f5ac59309 

 0xac77b44a5f3acc54e3844a609fffd64f182ef931 

 0xd7aa2bd9e9407f682a379bed346088b0849b6434 

 0x714dda349ef43326791f923e8389a21d11378c67 

 0xa3ce95ac672b62ed75afbe6f50285c28ef717a44 

 0xaade027d63ea859a4993961a8a8cc5aae3f020f3 

 Total Operation Scale(As of September 25th): ~$41 Million

 Blockscope's comprehensive forensics analysis indicates the attacker ultimately controlled approximately $41 million in realized proceeds from the combined treasury theft and minting operations.

 This figure represents ongoing analysis of complex multi-chain fund flows and may be subject to revision as additional evidence emerges.

 The minting wasn't monopoly money - it was a sophisticated multi-chain laundering operation worth tens of millions. 

 When you can create infinite tokens and successfully convert them to real ETH across multiple chains, who is counting losses and who is laughing? 

## The Hunter Becomes the Hunted

 Speaking of laughing and losses. 

 While the attacker was busy playing central banker with UXLINK's token supply, someone else was watching - and waiting. 

 At 02:15 UTC on September 23rd, cosmic justice arrived in the form of a phishing transaction: 

 0xa70674ccc9caa17d6efaf3f6fcbd5dec40011744c18a1057f391a822f11986ee 

 The UXLINK exploiter had fallen for the oldest trick in the Web3 book - a phishing attack.

 Scam Sniffer flagged the cosmic justice - one malicious "increaseAllowance" approval and 542 million UXLINK tokens vanished from the attacker's wallet.

 The tokens landed in addresses linked to Inferno Drainer - the notorious "draining-as-a-service" group that turns phishing into an art form.

 SlowMist’s founder Cos, confirmed what some suspected: the exploiter had been exploited by Inferno Drainer .

 Even experienced hackers aren't immune to clicking the wrong link. 

 What does it say about Web3 security when the people robbing protocols get robbed themselves? 

## The Ship is Sinking

 UXLINK spun into crisis mode , serving corporate speak while working behind the scenes. 

 First came the boilerplate “we’re working around the clock,” followed by the obligatory promise to call exchanges and freeze funds. 

 Then, the pivot to victim-blaming : don’t trade on DEXs, because “unauthorized tokens” are flooding the market.

 “We strongly advise all community members not to trade UXLINK on DEXs at this time, in order to avoid potential losses caused by these unauthorized tokens.”

 Translation: our token supply is completely screwed, please ignore the trillions of rogue tokens now floating free.

 Next up : the classic “majority of funds frozen” line - corporate code for “some exchanges helped, but most of the money is gone.” 

 Law enforcement got looped in, security experts were called, blockchain forensics firms were hired. 

 And then came their boldest move yet : a total token swap with a new fixed-supply contract.

 The plan was simple - abandon the compromised token, start fresh, roll out new tokenomics, and slap a shiny security promise on top.

 Just forget about those 10 trillion unauthorized tokens floating around like digital tumbleweeds.

 UXLINK stated : “We will promptly initiate a token swap plan to ensure the integrity of our token economy.” 

 Two days later, UXLINK rolled out their masterpiece: a shiny new contract that passed security audit , stripped of its mint function, and conveniently relocated to Ethereum instead of the compromised Arbitrum setup. 

 To dress it up, they added some regulatory compliance theater - name-dropping Korean authorities and boasting of “frozen hacker addresses”.

 Then came the migration plan . A 1:1 swap that excluded “illegally issued” tokens, but only for “legally issued” tokens. An on-chain redemption portal would arrive within five working days (from September 24th).

 Circulating supply was fixed at ~479M , based on the whitepaper.

 A follow-up announcement confirmed the Ethereum Mainnet relaunch with a hard cap of 1B tokens . It detailed both CEX and on-chain swap mechanics, and sketched out the compensation plan. 

 Frozen hacker tokens would remain off-limits. But users caught in the chaos might be reimbursed through buybacks, staking perks, or trading incentives - all depending on how much value UXLINK could claw back from the laundering trails.

 Meanwhile, security firm Guardrail AI couldn't resist the "we could have prevented this" victory lap, claiming their monitoring would have caught the unauthorized minting before it spiraled into token hyperinflation.

 Easy to be smart after the damage is done. 

 When your solution to a hack is to delete the entire token and start over, how badly did you mess up the first time? 

 UXLINK's $41 million heist serves up a familiar menu of administrative failure with a side of poetic justice. 

 UXLINK's token took a 70% nosedive from $0.30 to $0.072, wiping $70 million in market cap off the books while trading volume surged over 1,320% to $437 million as panic sellers raced for the exits. 

 But here's what really stings: we may never know exactly how the attacker gained admin access in the first place.

 Was it a phished team member? A malicious insider? Compromised infrastructure?

 UXLINK isn't saying, and maybe never will. Only time and a proper post-mortem can tell.

 Code exploits get detailed post-mortems because protocols want to look smart - "here's the bug, here's the fix, trust us with your money again."

 But admin key compromises get buried under corporate speak and damage control because admitting your humans are the weakest link doesn't inspire confidence. 

 Flash loan attacks teach us about slippage and oracle manipulation. Reentrancy bugs show us the importance of checks-effects-interactions.

 Smart contract exploits evolve the entire ecosystem forward.

 Private key leaks just leave us guessing whether someone clicked the wrong link or decided to get rich quick. 

 And if the people holding the keys can’t be trusted, who really owns anything on-chain? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] KiloEx exploit: KiloEx just learned the hard way that fancy multi-chain deployments don't protect you from basic security flaws

## Summary
Severity: High
Target: KiloEx
Loss: $7,491,500
Published: 4/14/2025
Source: https://rekt.news/kiloex-rekt
Type: rekt-postmortem

## Details
## KiloEx - Rekt

 Thursday, April 17, 2025 KiloEx - Defi - Oracle Manipulation 

 read this article also in : 

 KiloEx just learned the hard way that fancy multi-chain deployments don't protect you from basic security flaws. 

 Their multi-chain perpetual protocol lost almost $7.5 million after an attacker slid into their oracle's code with a wallet funded through Tornado Cash. 

 One minute you're celebrating your Binance backing, the next you're begging a faceless hacker to accept a 10% bounty and return your users' funds.

 While the team was busy expanding across Base, BNB Chain, and Taiko, they somehow missed the gaping hole in their oracle implementation that practically screamed "rob me."

 The attacker didn't need some novel zero-day exploit - just the digital equivalent of walking through an unlocked front door. 

 When will protocols learn that having "Kilo" in your name doesn't automatically give you the heavyweight security needed in DeFi's bloodsport arena? 

 Credit: Chaofan Shou , Cyver’s Alerts , KiloEx , SlowMist , ScaleBit 
 Price manipulation? More like price annihilation. 

 Security engineer Chaofan Shou sounded the first alarm on April 14th - "KiloEx_perp is hacked. $6M+ loss already. Likely due to price oracle access control issues."

 Minutes later, Shou confirmed the fatal flaw - "Anyone can change Kilo's price oracle."

 Twenty minutes after Shou's alert, Cyvers Alerts confirmed the bloodbath - "$7M HACK ALERT" across multiple chains.

 The attack had already metastasized from BNB to Base to Taiko, funds draining like a punctured artery.

 KiloEx acknowledged the security incident hours later, suspending platform usage and working with security partners to trace the flow of funds. 

 Ready to measure just how lightweight KiloEx's security really was? 

## Inside the Exploit

 No fancy zero-day needed when the front door's wide open. 

 KiloEx made stealing almost $7.5M easier than creating a new crypto wallet. 

 SlowMist's autopsy reads like a comedy of errors.

 Their "security" boiled down to a MinimalForwarder contract with security so minimal it didn't bother checking who was actually calling it.

 Four contracts linked together like a flimsy paper chain, each assuming the other would check IDs.

 KiloPriceFeed trusts Keeper. Keeper trusts PositionKeeper. PositionKeeper trusts MinimalForwarder. 

 And MinimalForwarder? MinimalForwarder? It trusts anyone with a forged signature and zero data validation. 

 The attacker walked right in, cranked ETH prices down to $100, opened leveraged longs, then jacked prices to $10,000. Cash out. Repeat.

 Base chain alone hemorrhaged $3.12 million through a hole so obvious it might as well have had a neon sign.

 Don't blame the Pyth Network’s oracle for this mess. KiloEx's implementation made a TSA checkpoint look airtight by comparison. 

 How does a $7.5 million heist move through crypto's dark alleys without leaving footprints? 

## Following the Stolen Loot

 Tornado Cash, crypto's favorite mixer turned digital laundromat. 

 That's where our attacker's wallet first popped onto the blockchain radar on April 13th - a full day before turning KiloEx into their personal money printer. 

 Funding from Tornado Cash: 

 0xa0fa4ab8ded0c07085d244e1981919b440f78b609e1cf8d7f8ee32d358dfdf46 

 The exploiter knew exactly what they were doing.

 Base, BNB Chain, Taiko, opBNB - all hit with precision timing that would make Swiss watchmakers jealous.

 Same vulnerability, different chains, just under $7.5M gone.

 Attacker's Addresses on Ethereum: 
 0x00fac92881556a90fdb19eae9f23640b95b4bcbd 

 After receiving funding through Tornado Cash on Mainnet, the exploiter began their massacre…

 Attacker’s Address on Base: 

 0x00fac92881556a90fdb19eae9f23640b95b4bcbd 

 Base Attack Transaction 1 ($3.13M): 0x6b378c84aa57097fb5845f285476e33d6832b8090d36d02fe0e1aed909228edd 

 Base Attack Transaction 2 ($187k): 
 0xde7f5e78ea63cbdcd199f4b109db2a551b4462dec79e4dba37711f6c814b26e6 

 Base Attack Transaction 3 ($11k): 
 0xf0fcce0807a82041d050a60461e187f0e81a6f7fbda69bb600c04049d924e138 

 Attacker’s Address on BNB: 

 0x00fac92881556a90fdb19eae9f23640b95b4bcbd 

 BNB Attack Transaction ($893k): 
 0x1aaf5d1dc3cd07feb5530fbd6aa09d48b02cbd232f78a40c6ce8e12c55927d03 

 BNB Attack Transaction 2 ($10k): 

 0x38b25be14b83fd549d5e0b29ba962db83d41f5f9072d0eac4f692fa8e7110bc0 

 Attacker’s Address on opBNB: 

 0x00fac92881556a90fdb19eae9f23640b95b4bcbd 

 opBNB Attack Transaction 1 ($2.9M): 0x79eb28ae21698733048e2dae9f9fe3d913396dc9d93a0e30d659df6065127964 

 opBNB Attack Transaction 2 ($205.5k): 
 0xcfc679a66f1d2966dbe83bb827409c40f29f881c20128107ae73e93ab55c65e4 

 opBNB Attack Transaction 3 ($14k): 
 0x783d56ce53af6d59c7c4be374ff48a66257733fadf5905526b5862a54917889f 

 Attacker’s Address on Taiko: 

 0x00faC92881556A90FdB19eAe9F23640B95B4bcBd 

 Attack Transaction on Taiko ($41k): 

 0x9bce6e105cea138fe9fb1e4bfb63fe90d21817db9d2cc6d1bf7697317430215b 

 Attacker’s Address on Manta: 

 0xd43b395efad4877e94e06b980f4ed05367484bf3 

 Attack Transaction on Manta ($100k): 

 0x06074831103a1e91c7b6dcb3b641cf4b79bfa208ea75e99cf9b5100d60a82df5 

 The following address was used to bridge funds … 

 Ethereum Address 1: 
 0x551f3110f12c763D1611d5A63B5F015d1c1a954C 

 Total Stolen: Roughly $7,491,500 

 By the time SlowMist's MistTrack flagged these addresses, the digital getaway car was already crossing blockchain bridges.

 zkBridge, deBridge, Meson - the shadowy cross-chain infrastructure that once promised DeFi's borderless future now serves as the perfect escape route for stolen funds.

 KiloEx immediately urged "all partner protocols and platforms to blacklist this address" while they worked with security partners to trace funds. A familiar script in DeFi's theater of exploits. 

 When your security gets violated this badly, what's left besides sending a strongly worded letter to the blockchain void? 

## The Aftermath

 "We regret to inform you that the KiloEx Vault has been exploited." No shit. 

 KiloEx's response hit all the classics - suspend trading, blacklist addresses, trace funds. 

 The digital equivalent of installing home security after the robbers already left with your TV.

 The next day came the technical revelation everyone already knew: "The vulnerability has been identified and is expected to be fixed soon."

 Congrats on the discovery that your front door was hanging off its hinges.

 Then the ritual hostage negotiation letter . Return 90% of the stolen $7.5M, keep 10% as your "whitehat bounty," and we'll even tweet about your cooperation! How generous.

 Their message to the attacker oozed desperation disguised as strength: 

 "Our investigation, supported by law enforcement, cybersecurity agencies, and multiple exchanges & bridge protocols, has uncovered critical information about your activities." 

 Translation: Please give our money back.

 The attacker's response? Complete silence so far. Their wallets sit undisturbed, $7.5M heavier.

 KiloEx filed a police report in Hong Kong and claims to be working with both Criminal Division, Cybercrime Unit, and SlowMist.

 They're freezing positions based on pre-hack snapshots and promising compensation plans while sending on-chain messages to the hacker.

 Strangely, KiloEx felt compelled to address "rumors suggesting KiloEx may have been involved in the hack" - rumors that barely existed before they mentioned them. 

 Why draw attention to an inside job theory nobody was pushing? 

 Was KiloEx audited ? Yes.

 5 Audits since June 2023.

 Did the audits help prevent this exploit? No.

 ScaleBit - KiloEx's most recent audit partner ( March 2025 ) - mastered the art of the sympathetic sidestep .

 They were "deeply saddened" about the incident while clarifying that "the root cause falls outside the scope of our audit."

 How convenient that the exact vulnerability that matters seems to be "out of scope." 

 If your security audit doesn't cover the front door, what exactly are you paying for? 

 Oracle manipulation - the exploit that launched a thousand post-mortems. 

 KiloEx joins the ever-growing graveyard of protocols that chose multi-chain deployment before securing their front door. 

 KiloEx deployed across four chains with the MinimalForwarder sitting unguarded at the gateway to $7.5 million in user funds.

 Five audits later, and the protocol still managed to miss what tried to sink their battleship.

 Expansion to multiple chains before fixing basic security? Pure crypto. 

 Patching code after $7.5M disappears? Too little, too late.

 Users don't care about post-mortems when their funds are gone.

 They care about security that actually works, not "deeply saddened" audit partners with convenient scope blindness. 

 What good is a MinimalForwarder when it forwards your entire treasury to hackers? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [C] Cork Protocol exploit: Fake tokens just popped the Cork protocol for $12 million

## Summary
Severity: Critical
Target: Cork Protocol
Loss: $12,000,000
Published: 5/28/2025
Source: https://rekt.news/cork-protocol-rekt
Type: rekt-postmortem

## Details
## Cork Protocol - Rekt

 Friday, May 30, 2025 Cork Protocol - Rekt - Defi 

 read this article also in : 

 Fake tokens just popped the Cork protocol for $12 million. 

 The attacker deployed a counterfeit contract and manipulated Cork Protocol’s exchange rate calculations by abusing its fallback mechanisms and unchecked token interactions - turning the protocol’s assumptions into a devastating exploit. 

 Cork's wstETH market got gutted by an exploit so surgically precise it made their security look like amateur hour.

 While the team panic-paused contracts and tweeted damage control, thousands of wstETH were already converted and quietly moved out of the protocol.

 Cork's smart contracts were supposed to compute exchange rates, not hand out free money to anyone with fake tokens and a calculator.

 The protocol learned that when you build your house on trust-but-don't-verify, eventually someone shows up with counterfeit keys. 

 If your exchange rate calculations can be gamed by fake tokens, who’s really in control? 

 Credit: Blockaid , Cyvers , MistTrack , Phil Fogel , Cork Protocol , William Li , Dedaub , Lei Wu , Three Sigma 
 Cork Protocol's Wednesday morning went sideways fast on May 28th. 

 Blockaid’s exploit detection system was triggered - an attacker deployed fake token contracts to manipulate Cork Protocol’s exchange.

 The attackers weren't subtle about it. Deploy malicious contract, manipulate exchange rates with fake tokens, drain 3,761 wstETH, convert to ETH, in a vicious one-two punch.

 Cyvers was on the scene : A malicious contract was deployed by an address likely funded by a service provider. 

 Funding Wallet: 
 0x47713cb34fabd63b39d7c5c6f675dca39d22762b 

 MistTrack identified the exploiter and traced the gas fees back to Swapuz , a supposed “service provider.”

 Phil Fogel, Cork's co-founder, delivered the inevitable damage control tweet : "We are investigating a potential exploit on Cork Protocol and are pausing all contracts. We will report back with more information."

 Shortly after, Cork confirmed what everyone already knew - the damage was clear: $12 million in wstETH had vanished, converted to ETH faster than Cork's team could tweet "we're investigating." 

 When the system can’t tell fake from real, how does an attacker turn counterfeit contracts into cold, hard ETH? 

## The Anatomy of a Fake Token Heist

 So how do you turn counterfeit contracts into $12 million in real assets? 

 According to security researchers, the exploit wasn't rocket science - just weaponized arithmetic and a protocol that couldn't tell fake tokens from real ones. 

 The attacker's playbook was elegantly simple: deploy fake token contracts, feed them into Cork's exchange rate calculations, and watch the protocol's fallback logic hand over the keys to the kingdom.

 Dedaub cut straight to the chase : "The root cause appears to be an issue in the way an exchange rate is computed. The attacker manipulated this by deploying fake tokens - the protocol contained logic to revert to a default value."

 Lei Wu from BlockSec pinpointed the exact failure: "It appears that the protocol fails to properly verify the arguments passed to the CorkCall function, allowing the attacker to specify a fake paymentToken and profit from it."

 William Li broke down the exploit like a magician revealing the sleight of hand. 

 The attacker didn't crack Cork's code - they played by the rules, just better than Cork did. 

 Cork allowed users to create markets with arbitrary redemption assets (RA) through the CorkConfig contract. The attacker exploited this by setting DS tokens from a legitimate market as the RA in their fake market.

 The exploit hinged on two critical flaws: Cork's CorkHook contract's beforeSwap function could be called by any user without authorization, and it accepted custom hook data for CorkCall operations.

 They created a fake market where a real DS token from the original market was treated as a base asset (RA). Cork's system never questioned it.

 The attacker manipulated the protocol by depositing valid DS tokens from a legitimate market into their new market as RA , receiving the corresponding DS and CT tokens in return. 

 Imagine a vending machine that gives you chips for inserting a fake chip bag - because it doesn't care what goes in, only that something does. 

 With those newly minted fake tokens, the attacker cycled back into the system, redeemed them through the legit PSM, and walked away with real wstETH.

 Free tokens in, real assets out. A depeg insurance protocol undone by a logic depeg.

 The protocol's mathematical assumptions met reality - and reality had fake tokens and a calculator. 

 But when you've just printed yourself $12 million in freshly minted ETH, where exactly do you take it to cash out? 

## Following the Digital Breadcrumbs

 Every blockchain heist leaves a trail - the trick is following it before it disappears into the crypto washing machine. 

 Attacker Address: 
 0xEA6f30e360192bae715599E15e2F765B49E4da98 

 Attacker’s Malicious Callback Contract: 
 0x9Af3dCE0813FD7428c47F57A39da2F6Dd7C9bb09 

 Victim Contract: 
 0xccd90f6435dd78c4ecced1fa4db0d7242548a2a9 

 Exploit Transaction 1: 
 0xfd89cdd0be468a564dd525b222b728386d7c6780cf7b2f90d2b54493be09f64d 

 Exploit Transaction 2 (Main theft): 
 0x605e653fb580a19f26dfa0a6f1366fac053044ac5004e1b10e7901b058150c50 

 Transaction tracing on Metasleuth here . 

 The attacker's methodology was textbook crypto crime 101: convert stolen assets into something liquid, move fast, leave no forwarding address. 

 All 3,761 wstETH got converted to ETH in a series of rapid-fire transactions - because when you're running a heist, stablecoins and blue chips don't ask awkward questions.

 Professional preparation for a professional payout.

 As of the last check, the stolen funds were still sitting pretty in the attacker's wallet - $12 million in ETH just waiting for its next move. 

 Did the attacker just get lucky - or were they already watching Cork's every move? 

## Audit Blindspot

 Cork Protocol wasn't some fly-by-night operation running unaudited code in the wild. 

 They had the full security theater package : audits from Quantstamp , Cantina , Sherlock , and Runtime Verification - four different firms, multiple rounds of reviews, even a bug bounty through Cantina , all the badges and certifications a DeFi protocol could want. 

 At least three of the four audit firms - Sherlock, Runtime Verification, and Quantstamp - had the vulnerable CorkHook contract outside their defined scope.

 Only Cantina's scope boundaries remain unclear, but somehow a critical input validation flaw in the core hook mechanism slipped through four separate security reviews.

 But as more details began to emerge, one thing stood out loud and clear.

 Sherlock’s team pointed out : "The exploit involves the CorkHook contract which we didn't audit." 

 Out of scope. The three most expensive words in DeFi security. 

 The recent exploit breakdown by Three Sigma revealed that Runtime Verification clarified their constraints: "This was a time-constrained verification effort, which means we had to make assumptions to handle the desired scope. Creating markets was a permissioned process at the time of verification. Verification of hook functions was out of scope, again due to time constraints."

 The vulnerability wasn't lurking in some cryptographic labyrinth or hiding behind advanced math - it was sitting in code marked 'out of scope' due to time constraints and audit boundaries.

 Cantina's audit specifically focused on input validation flaws, finding multiple instances where Cork failed to verify tokens properly - yet the critical vulnerability went undetected. 

 Maybe Cork's inevitable post-mortem will explain how four security firms managed to collectively miss the front door while checking every window.

 Cork burned months and serious cash getting their contracts rubber-stamped by premium auditors, then watched $12 million evaporate through the one door nobody checked.

 Four audits. Four firms. One gaping hole where the CorkHook contract should have been reviewed. 

 When your audit coverage has more gaps than a hockey player's smile, who's really protecting whom? 

 Fake tokens just taught Cork Protocol that trust-but-don't-verify is a $12 million philosophy. 

 The attacker didn't need zero-days or advanced cryptography - just counterfeit contracts and a protocol dumb enough to treat every token like a VIP at the vault door. 

 Cork's CorkHook contract became a validation-free zone dispensing fake tokens to anyone smart enough to call beforeSwap with malicious parameters, while four separate audit firms somehow missed the one piece of code that actually mattered.

 The protocol that wanted to insure users against depeg events couldn't insure themselves against fake tokens and missing input validation.

 Cork learned that premium auditors and institutional backing mean nothing when your core functions don't verify what tokens they're actually processing. 

 When your depeg insurance protocol gets depegged from reality by fake tokens, who's insuring the insurers? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

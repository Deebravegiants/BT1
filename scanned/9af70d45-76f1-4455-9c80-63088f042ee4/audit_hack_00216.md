# [H] ResupplyFi exploit: Hours matter in DeFi - and for ResupplyFi, two hours was all it took to turn a governance celebration into a $9.8 million funeral

## Summary
Severity: High
Target: ResupplyFi
Loss: $9,800,000
Published: 6/25/2025
Source: https://rekt.news/resupplyfi-rekt
Type: rekt-postmortem

## Details
## ResupplyFi - Rekt

 Friday, June 27, 2025 ResupplyFi - Rekt - Defi 

 read this article also in : 

 Hours matter in DeFi - and for ResupplyFi, two hours was all it took to turn a governance celebration into a $9.8 million funeral. 

 June 25th started with excitement over their latest market launch. 

 Their lending protocol got hit by an attacker who transformed a donation of crvUSD into a $9.8 million loan using nothing but mathematical sleight of hand and a vault so fresh it still had that new deployment smell.

 By evening, BlockSec was tweeting damage reports while the attacker vanished with enough stolen funds to buy a mansion.

 This wasn't some sophisticated exploit requiring months of research. 

 Just an old-school ERC4626 donation attack hitting a market deployed mere hours before the bloodbath.

 ResupplyFi had governance votes, audit reports, and all the usual DeFi compliance checkboxes.

 What they didn't have was protection against someone donating pocket change to manipulate their exchange rates into mathematical oblivion. 

 When your lending protocol gets annihilated by a textbook donation attack, maybe someone should start reading the textbook? 

 Credit: Blocksec Phalcon , Peckshield , ResupplyFi , Chaofan Shou , Beosin , TenArmor , CoinBench , Tony Ke , Decrypt , OKX Explorer , Certik , Michael Egorov , Aero , Leviathan News , Quill Audits 
 [The article has been updated. After conversations with both audit firms & ResupplyFi, the scope situation proved more complex than initially understood. We appreciate the professional dialogue with all parties. Rekt remains committed to accurate reporting & supporting builders.] 

 ResupplyFi's disaster movie started late in the day with BlockSec Phalcon dropping the first bomb . 

 "Alert! Phalcon system detected an attack transaction to @ResupplyFi caused ~9.8M USD loss."

 A few moments later, PeckShield confirmed the worst - another protocol got rekt.

 By the time the security cavalry arrived with their damage assessments, the attacker had already completed their digital heist and disappeared into crypto's favorite washing machine.

 BlockSec didn't mince words about the culprit: "Yet another lending protocol exploited via exchange rate manipulation on low-liquidity—even empty—markets!" 

 Empty markets. Fresh deployments. Classic ERC4626 donation attacks. 

 ResupplyFi had stumbled into DeFi's most predictable tragedy - launching an unprotected vault and watching someone else cash out first.

 Two hours after confirming the bloodbath, ResupplyFi finally surfaced with their damage control statement: "Resupply has experienced an exploit in the wstUSR market. The affected contract has been identified and paused."

 Paused. Past tense. After $9.8 million had already walked out the door. 

 Ready to see how a modest donation became a multi-million dollar withdrawal slip? 

## The Mathematics of Mayhem

 ResupplyFi's incident reads like a textbook case study in why empty ERC4626 vaults could be financial suicide machines. 

 Step one: Target a freshly deployed market. According to Chaofan Shou , the cvcrvUSD vault had been live for exactly two hours - barely enough time for the deployment transaction to cool down, let alone accumulate any meaningful liquidity.

 Step two: Execute the donation attack. As Beosin and TenArmor detailed, the attacker transferred 2,000 crvUSD directly to the vault controller, then minted just 1 wei of shares. This created a share price so astronomically inflated it broke ResupplyFi's exchange rate mathematics. ( Technical breakdown by CoinBench here )

 Step three: Watch the protocol commit financial suicide. According to Tony Ke's analysis , ResupplyFi calculated exchange rates using the formula 1e36 / oracle.getPrices(). When the oracle correctly reported the inflated vault price (2*10^36), the division rounded down to zero due to floor division.

 Exchange rate equals zero. Loan-to-value ratio equals zero. Borrowing limits? What borrowing limits? 

 According to OKX Explorer , the attacker deposited 1 wei of cvcrvUSD as collateral and borrowed $10 million reUSD - the protocol's entire available liquidity.

 As Cyvers detailed it in Decrypt’s piece on the exploit : "The attacker manipulated token prices, triggering a bug (zero exchange rate) in Resupply's smart contract, letting them borrow a ton of money for almost nothing."

 ResupplyFi's smart contracts had just approved an almost $10 million loan backed by pocket lint.

 Sometimes the most devastating attacks are the most predictable ones. 

 How do you trace a crime that leaves every fingerprint on an immutable ledger? 

## The Blockchain Autopsy

 Every heist needs funding, and this one started where many do - Tornado Cash. 

 Funding from Tornado Cash: 
 0x1962eb353a37ca816a6d967279dfdb005a640fe3b22ccb9e00939fe5810d8fb5 

 The attacker's preparation was pretty straight forward.

 Fund the operation through crypto's premier mixer, deploy a couple of contracts, then execute the mathematical massacre with surgical precision.

 According to CoinsBench's detailed analysis , the exploit began with the deployment of two specialized contracts at the start of the attack transaction. These weren't off-the-shelf tools - they were purpose-built for this specific heist.

 Attack Contracts are as follows… 

 Helper Contract 1(simple ETH receiver): 
 0xf90da523a7c19a0a3d8d4606242c46f1ee459dc7 

 Main Exploit Contract(orchestrated the entire attack): 0x151aa63dbb7c605e7b0a173ab7375e1450e79238 

 Attacker Addresses are as follows… 

 Attacker’s Primary Address: 
 0x6D9f6E900ac2CE6770Fd9f04f98B7B0fc355E2EA 

 Attacker’s Second Address (Holding $5.5 Million): 
 0x31129a5c13306A48E827e851D44E19Ca07d4928A 

 Attacker’s Third Address (Holding $3.9 Million): 
 0x886f786618623ffFB2be59830A47661Ae6492E16 

 According to CertiK , the attacker split the stolen funds between these two addresses - approximately $5.5 million to one wallet and $4 million to another, suggesting either profit-sharing with collaborators or enhanced laundering through multiple distribution paths.

 The exploit transaction: 0xffbbd492e0605a8bb6d490c3cd879e87ff60862b0684160d08fd5711e7a872d3 

 Targeted Contract: 
 0x6e90c85a495d54c6d7e1f3400fef1f6e59f86bd6 

 Targeted Contract Created a couple of hours before the exploit: 
 0x852eca15a9fd352817346915f7bc8817d46de349bd7a8fc6ee73c7b66ec9ab41 

 The transaction itself unfolds like a precision heist manual.

 According to QuillAudits' analysis , flash loan a modest 4,000 USDC from Morpho. Swap for crvUSD via Curve. Execute the donation attack that breaks the math. Borrow 10 million reUSD with worthless collateral.

 Convert everything back to ETH. Repay the flash loan. Keep the change. 

 When protocols promise security but deliver mathematical malpractice, who's really responsible for the cleanup? 

## Crisis Management Classics

 ResupplyFi's post-hack performance hit every note in DeFi's crisis management playbook. 

 First came the damage assessment - $9.8 million gone, but hey, "only the wstUSR market was impacted and the protocol continues to function as intended." 

 Then the investigation announcements. "A full post-mortem will be shared as soon as a complete analysis of the situation has been conducted."

 Michael Egorov from Curve felt compelled to distance himself: "There is no single person from Curve working on that project... don't generalize to Curve please."

 Fair enough - when your protocol gets nuked via donation attack, the last thing you want is guilt by association.

 With the damage done, attention turned to damage control and user compensation. 

 Meanwhile, the insurance fund quietly started covering losses. The cleanup effort expanded significantly when C2tP, from Convex, contributed $1.4 million of personal funds to cover user losses, followed by another $810,000 from Convex . 

 Combined with initial treasury payments of approximately $600,000, over $2.8 million has been repaid toward the $9.5 million loss.

 C2tP's personal sacrifice drew widespread praise , with the community noting "It's the kind of person he is" while acknowledging that user LP funds remained safe and untouched.

 The gesture highlighted both the human cost of protocol failures and the lengths some developers will go to protect their users. 

 Yet it also exposed an uncomfortable truth: when protocols fail, individual heroism becomes the last line of defense against user losses.

 The insurance pool mechanism sparked heated Discord and Twitter debates, with users discovering they'd joined without fully understanding how it worked.

 As one community member observed: "Folks joined the INSURANCE pool not reading how it worked. Insurance pool was used to cover bad debt." 

 When protocols depend on individual developers to save users from losses, is that risk management or just crossing your fingers? 

## Audit Autopsy

 ResupplyFi underwent security reviews by ChainSecurity and [yAudit] (now known as Electi)( https://github.com/resupplyfi/resupply/blob/main/audits/rsup_yaudit_report.pdf ) roughly 3-4 months before the hack - and this is where the story gets complicated. 

 Initially, both audit firms claimed the exploited market was outside their scope, deployed after their reviews concluded. 

 But after ResupplyFi's post-mortem challenged this narrative, a three-way conversation between Rekt News, the audit firms, and ResupplyFi revealed a more nuanced truth.*

 The vulnerable code pattern was actually in scope and audited.

 According to ChainSecurity: "The code of the vaults which were later deployed were in scope of the audits, the deployment of those vaults and ensuring that they are securely initialized wasn't in scope."

 The firm's trust model assumed "meaningful collateral" would be present on deployment - an assumption that proved problematic. 

 Electi confirmed they were "in the same boat" and clarified their position: "the deployment was not in scope but the underlying issue which is the price calculation rounding down to zero was in scope." 

 The gap appears to be between code review and deployment validation.

 As ChainSecurity noted, "it isn't standard yet to validate/audit deployments" - a potential blind spot when protocols deploy markets with different initialization parameters than anticipated.

 The situation highlights the complexity of security responsibilities in DeFi - where does the auditor's job end and the protocol's operational security begin?

 Both audit firms reviewed functional code that worked as designed, but deployment with zero collateral created conditions that enabled the exploit. 

 When audited code meets unexpected deployment scenarios, who's responsible for connecting those dots? 

 * [Details from three-way conversation between Rekt News, ChainSecurity, Electi, and ResupplyFi team members] 

 ResupplyFi's exploit reads like a DeFi case study in what happens when textbook vulnerabilities meet real money. 

 Deploy vulnerable vault, ignore donation attack vectors, watch attacker turn spare change into retirement money. The math was simple - the oversight was expensive. 

 Governance proposals passed, audit badges collected, markets launched. Everything looked professional until someone donated pocket money and borrowed the bank.

 Whether you call it an ERC4626 donation attack, vault inflation attack, or empty market rounding bug - the vulnerability remains the same: documented exploits with documented solutions.

 The post-mortem and subsequent conversations revealed the complexity of audit scope and deployment validation - questions about where responsibility lies when code passes review but deployments create unexpected vulnerabilities.

 ResupplyFi's experience shows how documented vulnerabilities can still slip through development processes.

 Two hours. Almost ten million dollars. One vulnerability that slipped through the cracks. 

 When sophisticated audit processes still leave room for exploitation, what does that tell us about the current state of DeFi security? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

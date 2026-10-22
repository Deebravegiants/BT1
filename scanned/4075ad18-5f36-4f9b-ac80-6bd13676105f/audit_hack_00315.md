# [H] Zoth exploit: Admin privileges - DeFi's favorite skeleton key for digital heists

## Summary
Severity: High
Target: Zoth
Loss: $8,400,000
Published: 3/21/2025
Source: https://rekt.news/zoth-rekt
Type: rekt-postmortem

## Details
## Zoth - Rekt

 Monday, March 24, 2025 Zoth - Rekt - Admin Privileges 

 read this article also in : 

 Admin privileges - DeFi's favorite skeleton key for digital heists. 

 Zoth watched $8.4 million vanish into digital mist when their contract authority fell into the wrong hands, turning a real-world asset protocol into real-world losses on March 21st. 

 A carefully orchestrated contract swap, executed with surgical precision, transformed Zoth's vaults into an express lane for outbound funds.

 Just three weeks after their March 1st $285k bloodletting, Zoth's March 21st dance with disaster proves some lessons cost more to learn than others.

 From contract compromise to complete liquidation in minutes - DAI harvested, ETH acquired, attackers vanished. 

 When your admin keys become someone else's skeleton key, who's really in control of your protocol's vault? 

 Credit: John Doe , SlowMist , Cyvers , Zoth , Securrtech , SolidityScan 
 When the digital knives come out, on-chain sleuths sharpen theirs. 

 John Doe was first on the scene , catching the exploit in real-time and flagging the attack before looping in SlowMist to sound the alarm.

 Security firms swarmed the blockchain wreckage.

 SlowMist confirmed the exploit - admin keys bled out, leaving the contract wide open for a precision swap that sealed its fate.

 Cyvers confirmed the kill shot moments later - pointing to the smoking proxy contract "USD0PPSubVaultUpgradeable," upgraded by the attacker's digital fingerprints just before the slaughter began. 

 The attack unfolded with mechanical efficiency - $8.4 million USD0++ tokens withdrawn, swapped for DAI, transferred to another address, all within minutes of the proxy contract upgrade. 

 Zoth's team finally surfaced , "Our system has experienced a security breach. We're actively investigating the incident and taking all necessary steps to resolve it as swiftly as possible."

 Securrtech carved the incident into bite-sized pieces - compromised wallet, swapped contract, and funds drained before anyone could blink.

 The blockchain breadcrumbs tell the story… 

 Attacker Address: 
 0x3b33c5Cd948Be5863b72cB3D6e9C0b36E67d01E5 

 Victim Address: 
 0x82f3a0392F58C50fa90542519832471BaE93e43e 

 Attack Transaction: 0x33bf669d125d11c432ac9b52b9d56161101c072fd8b0ac2aa390f5760fb50ca4 

 Final resting place: 
 0x7b0cd0D83565aDbB57585d0265b7D15d6D9f60cf 

 The attack - brutally effective, embarrassingly simple - another chapter in DeFi's never-ending admin key tragedy. 

 First the keys. Then the contract. Then the money. 

 Zoth's deployer wallet fell first.

 8.85 million USD0++ tokens ($8.4M) vanished within minutes.

 Convert to DAI. Transfer away. Ride off into the sunset. 

 No complex financial wizardry required - just god-mode admin access and stolen credentials. 

 When lightning strikes twice, the second bolt always hits harder.

 Zoth's March 1st encounter with hackers - a mere $285k flesh wound - seems quaint compared to today's $8.4 million slaughter.

 Their first exploit showcased actual technical skill - manipulating Uniswap V3 liquidity pools to exploit a logic flaw in LTV validation.

 The attacker gamed the system to mint ZeUSD without sufficient collateral backing. 

 SolidityScan - Zoth's own auditor - published a detailed analysis of that earlier breach, warning of validation vulnerabilities that remained wide open. 

 Yet three weeks later, Zoth's death came not through complex financial wizardry, but through the most pedestrian of exploits - compromised admin credentials.

 Same protocol. Different attack vectors.

 Same result - users' funds redistributed to attackers' wallets.

 An update from Zoth suggests this wasn’t just an opportunistic smash-and-grab. 

 The attacker stalked their prey for weeks, funding wallets and deploying contracts in multiple failed attempts before finally breaking through. 

 Asset issuers locked down 73% of Zoth’s TVL right after the breach, preventing an even bigger disaster.

 They have onboarded Crystal Blockchain BV to investigate and will share a detailed report in the coming weeks.

 The money’s gone, but Zoth isn’t ready to call it a loss just yet. 

 Protocols don’t beg, but they do bargain. 

 Zoth & Securr are putting up a $500k bounty - help track the $8.4M, and they’ll cut you in.

 Follow the breadcrumbs, submit your findings, and if the funds get frozen, you’ll walk away with 10% of the take.

 Yet as the bounty beckons, two hacks in three weeks can't be chalked up to mere misfortune. 

 Is it just bad luck or a glaring sign of systemic weakness? 

 Admin key compromises - DeFi's broken record that protocols keep dancing to. 

 No contract audit in existence could have saved Zoth from its $8.4 million digital execution. 

 The protocol's code wasn't the problem - the humans holding the keys were.

 A growing graveyard of protocols have been sacrificed at the altar of lax key management.

 The security theater continues - audits performed, vulnerabilities patched, while admin keys sit exposed like loaded guns on playground benches. 

 Perhaps protocols should start auditing the people who work for them - especially those whose fingerprints touch admin privileges.

 With each exploit, the script remains unchanged - one compromised key, one malicious contract upgrade, one unstoppable cascade of vanishing funds. 

 Trustless finance, they said. So why do protocols treat admin keys like party favors? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

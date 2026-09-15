# [H] AlexLab exploit: Another day, another private key was compromised

## Summary
Severity: High
Target: AlexLab
Loss: $4,300,000
Published: 05/14/2024
Source: https://rekt.news/alexlab-rekt
Type: rekt-postmortem

## Details
## AlexLab - Rekt

 Friday, May 17, 2024 AlexLab - REKT 

 read this article also in : 

 Another day, another private key was compromised. 

 AlexLab, the self-proclaimed finance layer on Bitcoin, had a few layers stripped, as a compromised private key led to a $4.3 million exploit on AlexLab’s XLink bridge on the BNB network. 

 Certik Alert caught a suspicious transaction affecting AlexLab on May 14th, with initial evidence pointing to a private key compromise.

 AlexLab did not officially confirm the exploit until the next day, where they stated that the misappropriated Alex Assets have been moved by the exploiter to major exchanges, where the assets were frozen by the exchanges.

 They offered a bounty equivalent to 10% of the stolen funds, with an expiration of May 18th at 0800 UTC. 

 Why did they wait a day until they made an official announcement about the exploit? 

 Credit: Certik , AlexLab , ImmuneBytes , Chain Aegis 

 The AlexLab team became aware of an exploit using compromised private keys obtained via a phishing attack. 

 In their official security update, they highlighted that the exploiter conducted a targeted attack, taking over as the admin of one of the vaults associated with ALEX liquidity pool.

 With the vault keys in hand, the attacker went buck wild, draining approximately 13.7 million STX from the compromised coffers . 

 Around 3 million of those pilfered STX were rapidly shot out to various centralized exchanges in a blatant cash-out attempt.

 The Alex team mobilized and managed to recover all aBTC, sUSDT, xBTC, xUSD, ALEX, atALEX, and a handful of other assets from the vault. 

 However, a sizable chunk of that STX loot managed to slip through the exchanges' hands before they could freeze the funds.

 According to further analysis by ImmuneBytes, the Deployer address carried out four malicious upgrades to the proxy contract associated with AlexLabs. 

 The upgrades caused the address of the bridge endpoint contract to change to unverified bytecode.

 Attacker address: 
 0x27055aE433E9DCb30f6EbCC1A374Cf5CC03C484E 

 Within an hour after the upgrade, the following withdrawals were made under these attack transactions.

 Attack Transaction 1: 
 0x94746d33792aeb27d2066b6d8f3c8a8c7410fe15c9500059f35e0b21c9bfb416 

 Attack Transaction 2: 
 0x47e123af93add709bc2516f6a5db057dfbb1d66a75b693cd7980cd3eb28c7357 

 A total of $4.3 million worth of digital assets were transferred to the following addresses.

 Stolen Funds sent to Address 1: 
 0xA747aF2a527E72cE303353b458a1c51eBCd53188 

 Stolen Funds sent to Address 2: 
 0x27055aE433E9DCb30f6EbCC1A374Cf5CC03C484E 

 A portion of the stolen funds have been identified and are in the process of being recovered from one CEX. 

 AlexLab is actively working through the required processes with other CEXs to claw back additional funds.

 They are now locked in a heated process of trying to retrieve the remaining STX and shared the current forensic data with all relevant CEXs.

 Since there is no assurance that all stolen funds will be recovered, they are evaluating deployment of ALEX reserves held by AlexLab Foundation towards funding of a treasury grant program to support their community impacted by the attack .

 In the meantime, they've got another Hail Mary in the works, possibly proposing that the Stacks community straight-up burn the unrecovered STX sitting in the exploiter's wallets, then reissue fresh tokens to the impacted users. 

 AlexLabs is currently working with all relevant parties on a detailed post-mortem report, which we will share with you very soon.

 ImmuneBytes and Chain Aegis have indicated that the attacker involved in this exploit was also involved in the attack on Mars Defi 412 . 

 Mars Defi 412 was attacked in a price manipulation attack for $100k on April 16th.

 AlexLab’s Security Audit page highlights that the Bitcoin Bridge is audited by CoinFabrik, covering both the contracts and the backends. The smart contracts are also subject to a bug bounty program on Immunefi.

 But it was a compromised private key that ultimately tried to blow up the lab, audits and bug bounties became an afterthought at that point. 

 The $4.3 million-dollar question remains: Just how did this sly exploiter manage to phish or finagle those highly-coveted vault keys? 

 The AlexLab team has their work cut out unraveling this $4.3 million private key caper. 

 While they've managed to recover some assets and freeze funds, millions are still sitting in the exploiter's shady wallets.

 Their proposed solutions of treasury grants and token reissuance show they're pulling out all the stops to make impacted users whole.

 But at the end of the day, that won't undo the damage of sloppy opsec that enabled this breach in the first place. 

 The day-long delay to make the exploit public is concerning. 

 As investigators dig deeper into the phishers' tricks or if this is a potential inside job, this saga will be a case study in the perils of private key mishandling.

 The crypto Wild West is an unforgiving place, one mistake is all it takes for your vault to get looted.

 AlexLab can audit and bug bounty till the cows come home, but they'd be wise to quickly implement multi-sig and other robust key management practices. 

 Otherwise, their shiny "finance layer" risks getting stripped bare by the next opportunistic vault raider.

 A raider who may be a repeat offender and is not afraid to use different attack vectors, who could be next? 

 The game of crypto cat-and-mouse wages on. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [C] Penpie exploit: The crypto world never sleeps and neither do its hackers

## Summary
Severity: Critical
Target: Penpie
Loss: $27,000,000
Published: 09/03/2024
Source: https://rekt.news/penpie-rekt
Type: rekt-postmortem

## Details
## Penpie - Rekt

 Wednesday, September 4, 2024 Penpie - REKT 

 read this article also in : zh 

 The crypto world never sleeps and neither do its hackers. 

 In the latest episode of "Who Wants to Be a Millionaire: DeFi Edition," Penpie has found itself on the wrong end of a $27 million exploit. 

 On September 3rd, a yield farming protocol, built atop the Pendle Finance ecosystem, learned a costly lesson in the dangers of complex financial integrations.

 As news of the exploit spread, the PNP token went into a free fall, tanking a brutal 40%, while the PENDLE token didn't escape unscathed, taking a 9% hit in the chaos.

 Another gentle reminder that in the high-stakes game of yield farming, sometimes the only thing you harvest is regret. 

 When the music stops in this high-risk DeFi dance, which investors will be left holding empty bags? 

 Credit: Chaofan Shou , Cyvers , Pendle , Penpie , PeckShield , Ancilia 
 The first signs of trouble came when Chaofan Shou raised the alarm on Twitter: "Seems like Penpie got hacked. $17M loss." 

 It didn't take long for the blockchain sleuths to mobilize, within 20 minutes, Cyvers confirmed the worst as the damage had ballooned to a staggering $27 million.

 Pendle Finance, the platform underlying Penpie, was quick to reassure users that their own funds were secure.

 Nevertheless, they hit the pause button on all contracts to further mitigate the damage.

 Penpie followed suit , admitting to a "security compromise" and freezing all deposits and withdrawals.

 In a space where code is supposed to be law, it seems some crafty lawyers found a loophole. 

 But in this digital courtroom, who's really calling the shots? 

 According to the blockchain gumshoes at PeckShield, the root cause was "the introduction of an evil market that was used to inflate the staking balance to claim unwarranted rewards."

 Translation for the non-tech savvy: the attacker created a fake Pendle market, essentially tricking Penpie's contracts into thinking they were dealing with the real McCoy. 

 Ancilia provided more information , highlighting that the exploit stemmed from a sneaky loophole in Penpie's batchHarvestMarketRewards() function. 

 In a flash, the attacker launched a reentrancy attack, creating a fake Pendle market to dupe Penpie's contracts.

 When the _harvestBatchMarketRewards() function called redeemRewards(), the hacker's contract slipped in, executing a deceptive maneuver that would make seasoned con artists envious.

 The end result? A textbook double-dip, inflating the attacker's staking balance and siphoning off undeserved rewards. 

 Exploit transaction: 0x56e09abb35ff12271fdb38ff8a23e4d4a7396844426a94c4d3af2e8b7a0a2813 

 Exploiter Addresses: 
 0x7a2f4d625fb21f5e51562ce8dc2e722e12a61d1b

 0xc0Eb7e6E2b94aA43BDD0c60E645fe915d5c6eb84 

 Fake Pendle Market: 

 0x0ab305033592E16dB7D8e77d613F8d172a76ddc9 

 Attack contracts: 

 Arbitrum: 0x4BC9815b859c8172CEe1ab2CD372fD0Eb00eb487 

 Ethereum: 0x4aF4C234B8CB6e060797e87AFB724cfb1d320Bb7 

 Despite audits by WatchPug and Zokyo , this glaring oversight slipped through the cracks.

 Penpie has posted a message to the hacker on Twitter, hoping to retrieve the stolen loot.

 Pendle posted a Post Mortem on behalf of Penpie on Twitter, where they mentioned the $105 million that wasn’t stolen, but failed to mention what was stolen and the specifics behind the exploit.

 Yet another reminder that even in the world of trustless systems, we're still putting an awful lot of faith in protocols to do their security due diligence.

 The exploiter, armed with nothing more than some clever code and a dash of audacity, managed to outsmart multiple layers of supposed security. 

 In this game of digital cat and mouse, are we building fortresses or just more elaborate mazes? 

 Penpie's misfortune serves as a stark reminder that in the wild west of DeFi, even the sharpest tools can get dulled. 

 It's a tale as old as time (or at least as old as smart contracts), in the rush to innovate, security sometimes takes a back seat. 

 As the DeFi space continues to evolve at breakneck speed, it's clear that even more rigorous security measures and audit processes are needed.

 But in a world where "move fast and break things" is the modus operandi, can we really expect protocols to pump the brakes? 

 Is it too much to ask protocols that hold millions in users funds to audit every upgrade?

 In this case, it appears so.

 For now, Penpie joins the ever-growing list of protocols that have fallen victim to exploits in the digital Wild West. 

 Is it time for DeFi protocols to prioritize security over speed, thoroughly auditing upgrades and fortifying defenses, or will they continue to gamble with user funds and leave themselves vulnerable to relentless blackhat gunslingers? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

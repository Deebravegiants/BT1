# [H] Astroport exploit: On July 30th, Astroport, a DEX on the Terra network, fell victim to a hack resulting in losses of roughly $6.4 million

## Summary
Severity: High
Target: Astroport
Loss: $6,400,000
Published: 07/30/2024
Source: https://rekt.news/astroport-rekt
Type: rekt-postmortem

## Details
## Astroport - Rekt

 Wednesday, July 31, 2024 Astroport - Rekt 

 read this article also in : 

 On July 30th, Astroport, a DEX on the Terra network, fell victim to a hack resulting in losses of roughly $6.4 million. 

 The attack exploited a vulnerability that was known and patched in April, only to be accidentally reintroduced in a June upgrade. 

 This oversight raises serious questions about the state of security practices in the wake of regulatory actions against Terraform Labs (TFL) by the SEC.

 The exploit sheds light on the complex interplay between regulatory actions and ecosystem security, highlighting potential gaps in the maintenance of critical infrastructure.

 It also underscores the importance of heeding security warnings and the need for robust processes to prevent the reintroduction of known vulnerabilities.

 This incident is more than just another entry in the long list of DeFi exploits, it's a stark reminder of the consequences of ignored warnings and regulatory actions.

 As the summer heats up, so does the frequency of crypto heists. 

 But when old bugs come back to haunt us and warnings fall on deaf ears, who's really to blame? 

 Credit: Rarma , Cyvers , Astroport , Terra , Jacob Gadikian , _gabrielShapir0 , Zaki Manian , FXStreet 

 Terra aka Luna is a name that instills nostalgia and PTSD, depending on who you ask. 

 Like a phoenix rising from the ashes of its algorithmic stablecoin disaster , Terra 2.0 promised a fresh start.

 But old habits die hard in the wild west of crypto and it seems some bugs are harder to kill than others.

 First reported by Rarma , as he poured one out for ASTRO holders, including himself, as he spotted millions flowing through suspicious transactions. 

 Astroport acknowledged the exploit shortly after.

 As the exploit unraveled, Terra's validators pulled the emergency brake, halting the chain . 

 In a twist of crypto irony, a critical IBC bug , once vanquished in April's emergency patch across Cosmos chains, rose from the dead in Terra's June upgrade. 

 Like a horror movie villain, the vulnerability came back with a vengeance, ready for its summer blockbuster debut.

 With the bug reintroduced, the stage was set for a classic crypto caper.

 The attacker, wielding the resurrected vulnerability like a cursed wand, took advantage of a reentrancy vulnerability in the timeout callback of ibc-hooks to conjure tokens out of thin air, leaving Terra's defenses in tatters. 

 The dark magic summoned a haul of 60 million ASTRO tokens, 3.5 million USDC, 500,000 USDT, and 2.7 BTC from the abyss, totaling roughly $6.4 million in ill-gotten gains at the time of the exploit. 

 Roughly 3.5 hours later after halting the chain, Terra's digital heart started beating again.

 The chain's emergency chain upgrade completed, transactions flowed once more through its veins.

 Validators holding over 67% of the voting power on Terra threw on their digital armor, upgrading nodes to fend off the exploit's encore, with more validators expected to upgrade soon.

 According to Astroport , the attacker's Terra address, hoarding 20 million ASTRO, was swiftly frozen by Astroport, leaving their loot as stagnant and lifeless as a tundra landscape. 

 The final tally? A whopping 58 million ASTRO tokens pilfered, with 33 million making a bridge trip to Neutron. 

 On Neutron, the stolen ASTRO tokens were removed from the exploiter’s wallet via TokenFactory Force Transfer.

 The remaining 20 million ASTRO on Terra? 

 Blacklisted faster than a Trumper in Hollywood. 

 ASTRO fell roughly 56% in the aftermath of the attack, according to Coingecko data .

 Attacker’s address on Terra: 
 terra1wrve5z5vsmrgy6ldcveq93aldr6wk3qmxavs4j 

 Attacker’s address on Neutron: 
 Neutron16wynag7xgfy35sp8c5ls25c0je7dydmvq5pnd8 

 They also bridged some funds to Ethereum and swapped to ETH. 

 Bridge transaction: 
 7E28A2BDD3A6DBED27269C23D0BDA2FBE4B2BE7F613E87CC23A237DA473F14E2 

 Address on Ethereum: 
 0xBDe173c4C2249d3a98cD6ed844a4421728114F5A 

 The boy who cried wolf, except the wolf was real. 

 In a twist that adds a layer of frustration to this incident, it turns out that vulnerabilities had been flagged by Jacob Gadikian, a former prominent figure in the Cosmos ecosystem. 

 Gadikian had recently highlighted the risks , but his warnings were largely dismissed by those in a position to act.

 "This is why I stopped: coordinated harassment endured while making security reports," Gadikian stated following the hack.

 Jacob even shared a solution to mitigate the issue.

 “When there's a security patch in comet, IBC, cosmos, etc, that shows in go.mod and that is why I automated it. This PR changes two files , go.mod and go.sum”

 Gadikian added , "If amulet were doing what I did, this would not have happened. It is trivial to set up monitoring for all cosmos chains based on go.mod. I know, cause I did." 

 His experience raises troubling questions about the ecosystem's approach to security and its treatment of those who raise alarms. 

 However, in an ecosystem as intricate and often contentious as IBC, it's important to note that there are often multiple sides to every story.

 Adding fuel to the dumpster fire, it seems Terra's dev team may have been taken out at the knees.

 As pointed out by gabrielShapir0 , Terra/TFL patched the vulnerability back in April, only to accidentally un-patch it in a later update. With TFL potentially running on a skeleton crew post-SEC action, such an oversight was perhaps inevitable.

 Zaki Manian confirmed , "Terra was part of the original vulnerability coordination but they accidentally reverted the patch in the June upgrade."

 The exploit's success may be partially attributed to the reduced capacity of the Terra team following the SEC's actions against Terraform Labs. 

 The SEC's actions, meant to protect investors, may have inadvertently left the henhouse door wide open. 

 gabrielShapir0 could not have summed it up better , the SEC shuts down TFL, no one is left to patch known a Terra vulnerability, someone mints infinite $ASTRO and dumps it to oblivion. Slow clap for the SEC.

 As the Astroport saga unfolds, we're left with a patchwork of patched and unpatched vulnerabilities, ignored warnings and regulatory aftershocks.

 Terra's phoenix-like resurrection seems to have inherited more than just its predecessor's name. 

 In this blockchain Groundhog Day of exploits and finger-pointing, how many more project implosions must we endure before crypto prioritizes unbreakable security over the blame game? 

 The Astroport exploit serves as a stark reminder of the fragility within our blockchain ecosystems. 

 From overlooked vulnerabilities to regulatory pressures, the crypto world faces challenges on multiple fronts 

 This exploit could have been prevented and there could likely be more than one party at fault.

 From developers reverting patches to ignored warnings and regulatory actions leaving projects understaffed.

 This tangled web of oversights and missteps reveals a systemic vulnerability in how the ecosystem approaches security.

 The IBC community now faces a crossroads.

 Will it continue down the path of reactive patches and finger-pointing or forge a new way forward with proactive security and collaborative problem-solving? 

 The stakes are high in defi, can we afford to keep treating security as an afterthought rather than a fundamental pillar? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

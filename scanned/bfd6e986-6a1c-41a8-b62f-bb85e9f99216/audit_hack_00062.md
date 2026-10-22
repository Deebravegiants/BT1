# [C] CoinDCX exploit: Transparency has a half-life of exactly 17 hours in CoinDCX time

## Summary
Severity: Critical
Target: CoinDCX
Loss: $44,300,000
Published: 7/18/2025
Source: https://rekt.news/coindcx-rekt
Type: rekt-postmortem

## Details
## CoinDCX - Rekt

 Tuesday, July 22, 2025 CoinDCX - Rekt - CEX 

 read this article also in : 

 Transparency has a half-life of exactly 17 hours in CoinDCX time. 

 Hackers siphoned $44.3 million from India's second-largest crypto exchange while management played mute for nearly a day - only breaking their silence after blockchain detective ZachXBT dropped receipts that forced their hand. 

 The attackers had methodically prepared their heist, routing 1 ETH through Tornado Cash, bridging funds across multiple chains, and executing a precision drain of CoinDCX's wallets.

 While $28.3 million in SOL and $15.78 million in ETH vanished into mixing protocols, CoinDCX's leadership was apparently practicing radio silence.

 Their damage control playbook read like a Mad Libs template: insert "sophisticated server breach" here, sprinkle "treasury reserves" there, and hope nobody noticed customers found out from ZachXBT instead of official channels. 

 When you need blockchain detectives to announce your own $44.3 million disaster, what exactly are you managing besides the cleanup? 

 Credit: ZachXBT , Cyvers , Sumit Gupta , BSC News , Neeraj Khandelwal , DL News , Breadcrumbs , CoinDCX 
 ZachXBT wasn't hunting for CoinDCX specifically - he was following breadcrumbs that Cyvers had flagged about suspicious withdrawals from an untagged wallet. 

 July 19th, 14:41 UTC, Zach dropped a bombshell in his Telegram channel : "Looks like the India centralized exchange 'CoinDCX' was likely drained for ~$44.2M almost 17 hours ago and has yet to disclose the incident to the community."

 The first transaction hit CoinDCX's Solana wallet on July 18th at 23:22 UTC - a $4.3 million goodbye kiss that nobody at the exchange seemed eager to discuss publicly.

 First Attack Transaction: 
 5mPfNreuEeNanMoxCtGuWWgw1pbpM7SXC7ZZJH9Z6qeGq7YgEsNPmXrZKhnJezFHZFcdronZJKaoGieXcg4S9sqx 

 ZachXBT's detective work revealed the attacker's money trail : 1 ETH from Tornado Cash funding the operation, stolen funds split across Solana addresses, then bridged to Ethereum. 

 The affected wallet wasn't even publicly tagged or included in CoinDCX's proof-of-reserves, forcing manual attribution through counterparty analysis.

 The timeline painted an uncomfortable picture. Attack begins Friday night, funds start moving, silence stretches through Saturday morning - then suddenly everyone's an expert on transparency once the cat's out of the bag.

 A fine example of "oh by the way, we got hacked" - nearly a day late and $44.3 million short. 

 When public disclosure comes 17 hours after the bleeding starts, who's really setting the transparency timeline? 

## Forced Transparency

 ZachXBT's Telegram post hit at 14:41 UTC on July 19th. By 14:48 UTC, CoinDCX CEO Sumit Gupta was suddenly ready to talk . 

 Seven minutes. That's how long it took for "we have always believed in being transparent with our community" to materialize after getting publicly called out. 

 Gupta's damage control statement read like crisis management bingo: "sophisticated server breach," "operational accounts segregated from customer wallets," "treasury reserves," and the classic "no customer funds impacted."

 Every box checked except the one that mattered - why customers heard about it from Twitter first.

 But the scrambling wasn't over. An hour later at 16:41 UTC, co-founder Neeraj Khandelwal announced : "Because of excessive load on the platform, Portfolio APIs are jammed." 

 Two minutes later, CEO Sumit Gupta chimed in with nearly identical messaging, adding a curious "PS: Customer assets remain safe!" 

 Funny how portfolio APIs crash an hour after announcing your hack. Still workshopping the cover story?

 ZachXBT wasn't buying the transparency theater. His response cut through the corporate spin : "Your team waited 17 hours to disclose (not until after it was alerted publicly)."

 The exchange's community management apparently went into overdrive, with team members reportedly asking users to thank Gupta for his "transparency" in Discord channels.

 Nothing says authentic crisis response quite like crowdsourcing gratitude for doing the bare minimum. 

 When your transparency only kicks in after getting exposed by blockchain detectives, is it really transparency or just damage control with better timing? 

## The Preparation Game

 July 18th wasn't day one - the real show started three days earlier when someone decided CoinDCX needed a $44.3 million haircut. 

 July 16th brought the opening move: 1 ETH sliding out of Tornado Cash like butter. 

 No direct routes here - the funds bounced through FixedFloat, took a vacation on Polygon, then bridged over to Solana via deBridge.

 Fixed Float Funding Transaction: 
 0x90083b839d093536104efb592aa46847993dca26a9410faac99aad4ec236f41b 

 Because why take the highway when you can take a scenic route through every blockchain in existence?

 July 17th may have been rehearsal day. Infrastructure setup, system testing, probably ordering pizza while mapping out which wallets to hit first. 

 This wasn't some weekend warrior looking for lunch money - someone was running a three-day clinic in exchange infiltration. 

 July 18th, 21:07 UTC: A single USDT test transaction. The digital equivalent of checking if the vault door is actually locked.

 Then the floodgates opened. Between 22:09 and 22:14 UTC, five minutes of systematic destruction : $2 million, $7 million, $10 million, $10 million, then two separate $5 million withdrawals, finishing with a final $5 million transfer.

 The stolen funds landed across multiple addresses:

 Solana #1: 
 6peRRbTz28xofaJPJzEkxnpcpR5xhYsQcmJHQFdP22n 

 Solana #2: 
 3btch8cSVp3Uh2SiY9DeiRNYUBmFiBNHZQzDyecJs7Gu 

 Ethereum (holding roughly $44.3 Million as of July 22nd): 
 0xEF0c5b9E0E9643937D75C229648158584A8CD8D2 

 Full Transaction Tracing through Breadcrumbs .

 The attackers didn't just steal - they performed financial surgery, carving out specific amounts with precision timing that suggests intimate knowledge of CoinDCX's systems. 

 When hackers spend more time planning your exploitation than you spent securing against it, who's really the professional here? 

## Bounty Hunters Wanted

 Monday morning brought CoinDCX's next act: the recovery bounty announcement that read like a desperate Craigslist ad for stolen goods. 

 "Up to 25% of any recovered funds will be awarded to individuals or teams who can help trace and retrieve the stolen crypto," CEO Sumit Gupta posted , apparently believing white hat hackers work on commission. 

 The messaging pivoted from transparency champion to victim advocate faster than a politician during election season.

 "More than recovering the stolen funds, what is important for us is to identify and catch the attackers," Gupta declared, as if catching cybercriminals had suddenly become their core business model.

 Co-founder Neeraj Khandelwal joined the chorus with his own bounty post , thanking a laundry list of security firms and foundations for their "support" - because nothing says crisis management quite like name-dropping your entire rolodex. 

 The exchange's $538.35 million in reserves supposedly absorbed the loss without breaking a sweat, yet here they were offering bounties like contestants on a game show.

 Either the treasury hit wasn't as painless as advertised, or someone really wanted those attackers caught.

 Both executives stressed the hack didn't impact customers or platform operations – corporate speak for "please don't withdraw your funds while we figure this mess out."

 Because obviously, a $44.3 million loss is just accounting noise, not a user concern. 

 When your post-hack strategy involves crowdsourcing detective work instead of explaining how you got breached, are you running an exchange or a puzzle contest? 

 July 2024: WazirX gets rekt for $235 million and plays dead until blockchain detectives drag them kicking and screaming into the light. 

 July 2025: CoinDCX bleeds $44.3 million and pulls the exact same vanishing act until ZachXBT forces their hand. 

 Déjà vu doesn't begin to cover it. More like déjà poo - same shit, different exchange.

 India's biggest exchanges have turned silence into an art form - why announce your own disasters when blockchain detectives will eventually do it for you?

 Both hacks followed the same script: attackers prep for days, execute like professionals, then watch management teams pretend transparency means talking only after getting caught.

 CoinDCX's seven-minute turnaround after ZachXBT's post wasn't confusion - it was panic about who controlled the narrative. 

 The was too clean to be random, yet management won't discuss internal investigations. 

 When you won't even confirm you're looking at your own employees, what else aren't you saying?

 The methodical preparation, cross-chain laundering, and surgical precision could hint Lazarus Group, according to some sources , the same state-sponsored crew that's been turning exchanges into personal ATMs across the globe.

 Meanwhile, CoinDCX leadership went from "we believe in transparency" to "please help us find our money" faster than their treasury absorbed a $44.3 million hit.

 Two major Indian exchanges, two massive hacks, two cases of transparency arriving only after public shaming. 

 When your crisis management playbook is hoping nobody notices until someone with better blockchain skills does your job for you, are you running an exchange or just playing hide and seek with other people's money? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

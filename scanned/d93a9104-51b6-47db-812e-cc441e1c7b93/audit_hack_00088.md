# [H] Dexible exploit: Crisis-comms calamity as cross-chain chaos continues…

## Summary
Severity: High
Target: Dexible
Loss: $2,000,000
Published: 02/17/2023
Source: https://rekt.news/dexible-rekt
Type: rekt-postmortem

## Details
## Dexible - REKT

 Monday, February 20, 2023 Dexible - REKT 

 read this article also in : zh 

 Crisis-comms calamity as cross-chain chaos continues… 

 The decentralised exchange aggregator, Dexible lost a total of $2M on Friday, on Ethereum and Arbitrum. 

 Although contracts were quickly paused, an official announcement came more than 9 hours after the hack, and over five hours after Peckshield raised the alarm .

 The thread states that their tech lead “ discovered the attack early on ” but that the “ Twitter channel was not able to respond in time ”, despite various promotional tweets being published in the intervening hours.

 When they did finally respond, however, part of their message came across as, at best, tone-deaf and, at worst, indifferent. 

 There's no excuse for an exploit, but these things happen

 And when called out , the Dexible team simply referred to rekt.news’ leaderboard , stating a hard truth:

 exploits happen in DeFi.

 Credit: Dexible, Peckshield , Beosin 

 One feature of Dexible’s recently introduced v2 contracts allows users to define their own routing via the selfSwap function. Dexible’s post-mortem report (published via Telegram and Discord, in PDF format) explains:

 embedded in each request to swap was a "route" of what DEX to call and what data to send to that DEX to execute a swap

 However, the function does not check whether the router address is actually a DEX by, for example, using an on-chain allowlist:

 the router address was not verified on-chain in any way. This meant that instead of calling a DEX smart contract, the hacker simply called a token contract with a request to "transferFrom" any account that had spend approval on the Dexible contract

 Attacker addresses ( ETH , ARBI , BSC ): 0x684083f312ac50f538cc4b634d85a2feafaab77a 

 Example tx: 0x138daa4c… 

 Relatively few addresses were affected, with the majority of losses reportedly coming from an address belonging to BlockTower Capital which lost 18M TRU tokens, valued at ~$1.4M at the time.

 In total, approximately $1.5M was lost on Ethereum, and sent to Tornado Cash. A further $450k was lost on Arbitrum, which was bridged to BSC before also being washed via Tornado Cash.

 In the post-mortem report, the Dexible team attempted to justify releasing unaudited code based on the experience of their team:

 A formal audit was not performed on the latest set of contracts. We had several community members and Dexible engineers review the code, and they did not find the vulnerability. The core engineer that created the contracts has over 25 years of software engineering experience, and he did not see the vulnerability. Upon reviewing one of the hacker's transactions, however, he immediately understood how it was executed.

 An audit is not a silver bullet… but it certainly helps. 

 Even the most experienced engineers may overlook a security vulnerability in their own code. Naturally, when building a new protocol, devs primarily have users in mind.

 But in this industry, security is paramount.

 And no shortage of unaudited protocols have made it onto the leaderboard . 

 In Dexible’s own words: 

 exploits happen in DeFi.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

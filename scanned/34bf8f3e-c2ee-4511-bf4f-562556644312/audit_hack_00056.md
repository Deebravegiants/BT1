# [C] bZx exploit: It may be their first time on our leaderboard, but this protocol has priors

## Summary
Severity: Critical
Target: bZx
Loss: $55,000,000
Published: 11/05/2021
Source: https://rekt.news/bzx-rekt
Type: rekt-postmortem

## Details
## bZx - REKT

 Saturday, November 6, 2021 bZx - REKT 

 read this article also in : zh 

 Attacks can come from all angles. 

 It may be their first time on our leaderboard, but this protocol has priors. 

 The debut entry for bzx.network goes straight into the top 10. 

 A bZx developer was sent a phishing email to his personal computer with a malicious macro in a Word document that was disguised as a legitimate email attachment, which then ran a script on his Personal Computer. This led to his personal mnemonic wallet phrase being compromised. 

 Before yesterday's events, the last incident to hit the project was in September 2020, when $8M was taken (and later returned).

 Previously, in February 2020, bZx fell victim to two attacks, in which $298,000 and $645,000 were lost to the first flash loan based exploits.

 Looks like 4th time’s the charm for bZx. 

 Given their chequered past, when the announcement came yesterday that the “ private key controlling the Polygon and BSC deployments was compromised ”, the replies were more of exasperation than of shock...

 "What is this like 4th time?" 

 "It’s probably time for you guys to just give up on this whole crypto thing. Y’all ngmi." 

 ~10 hours after the initial announcement, bZx published an update stating that one of their devs had fallen victim to a phishing attack, stressing that the code itself hadn’t been compromised... 

 Which was of little comfort for the users who lost their money. 

 Slowmist have been keeping a running total of funds lost, which at the time of writing is up to ~$55M.

 It’s hard to blame the team when the attack is so sneaky. Can bZx recover, or is this their fourth and final fatality?

 bZx have issued a preliminary post mortem , detailing the events and containing a list of addresses used by the hacker across Polygon , BSC ( 1 , 2 , 3 ) and multiple Ethereum addresses ( primary wallet ). 

 In place of the more technically advanced exploits that the protocol has faced in the past, this time the root of the issue was a simple phishing attack.

 Sometime before the exploit, a bZx dev was sent a phishing email with an attached Word document containing a malicious macro. Opening this document resulted in the dev having the keys to their personal wallet compromised.

 But this was not a personal attack. This EOA had control over bZx’s Polygon and BSC deployments. 

 The hacker was therefore able to gain control of the contracts and drain them of BZRX . The code was then updated to enable the extraction of tokens from any wallet which had granted token approvals to the affected contracts.

 Check your token approvals here: Polygon , BSC 

 List of bZx contracts 

 Despite bZx’s attempts to convince the community that the damage was contained to just Polygon and BSC, the hacker then sent stolen BZRX to Ethereum to use as collateral and borrow a variety of other assets.

 Though the attacker nets less profit this way, they also find a way around the liquidity problem of attempting to dump such a large quantity of BZRX.

 bZx state that they have reached out to centralised services, requesting that Circle freeze the stolen USDC, while the funds on Binance as well as USDT were quickly frozen.

 They have also reached out to the hacker offering to “ chat and reach an agreement ”

 The fact that such a large loss of funds can be attributed to such a simple attack vector is hard to believe, especially for a protocol that has experienced more than their fair share of security issues in the past. 

 Anyone in crypto should be expected to be wary, and devs working on high TVL projects especially so. But human error in this case should never have been able to lead to such an enormous loss .

 But does all the blame lie with the protocol? 

 Losing control of contracts due to their being vulnerable to a single EOA security breach is unimaginable for any responsible project, and there is no room for “ incompetence or negligence ” when $55M is at stake.

 That being said, it takes an especially callous and greedy hacker to go on to drain individual users’ wallets after having extracted millions.

 So long rekt readers. 

 Until next time, bZx... 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

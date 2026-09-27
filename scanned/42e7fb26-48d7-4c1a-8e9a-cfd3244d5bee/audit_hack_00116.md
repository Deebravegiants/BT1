# [H] Gym Network exploit: Gym Network offers a “ perfect workout for your tokens ”, but has pushed itself to failure

## Summary
Severity: High
Target: Gym Network
Loss: $2,100,000
Published: 06/08/2022
Source: https://rekt.news/gymnet-rekt
Type: rekt-postmortem

## Details
## Gym Network - REKT

 Friday, June 10, 2022 Gym Network - BSC - REKT 

 read this article also in : zh 

 Gym Network offers a “ perfect workout for your tokens ”, but has pushed itself to failure. 

 A recently introduced feature led to a loss of $2.1M from the project, crashing the price of GYMNET as the stolen tokens were sold off.

 The official announcement states that the team has already fixed the issue and plans to recover losses .

 The project’s two audits were completed last month. 

 Why introduce new code so soon and risk an injury? 

 Credit: Peckshield , Beosin 

 The BSC-based yield aggregator, built on top of Alpaca Finance, introduced a vulnerable “Claim and Pool” feature in its updated Single Pool Contract two days ago.

 Peckshield states that:

 The bug is due to the lack of caller verification, which is exploited to increase the balance without making any payment.

 This allows the hacker to create fake deposits to the contract, which are processed despite the attacker not spending any coins. The hacker can then simply withdraw their balance of falsely credited deposits.

 Exploiter’s address: 0xb2c035eee03b821cbe78644e5da8b8eaa711d2e5 

 Example exploit tx: 0x8432c1… 

 The attacker was funded via Tornado Cash, and their exploit contracts swapped the stolen GYMNET into a total of ~7.5k BNB .

 2k BNB (~$570k) sent to Tornado Cash

 3k BNB (~$855k) remain on the exploiter’s BSC address 

 2.5k BNB swapped to 387 ETH (~$700k) and bridged to ETH address 

 Gym Network was quick to confirm the source of the vulnerability, posting the following message in their Telegram group.

 Although GYMNET dropped ~90% as the exploiter dumped the stolen tokens, it has since recovered to ~70% of its pre-hack price. 

 The project was audited by both Certik and Peckshield in May, however the faulty code was introduced two days ago.

 Why carry out two audits if you’re going to change the codebase a month later? 

 Was this the plan all along? 

 The popularity of BSC among retail users has led to many low-effort projects with weak security, and some projects have been rekt multiple times . 

 But the timing of this hack comes at a time when Binance itself is in the spotlight, with pressure coming from multiple fronts.

 On Monday, it was reported that an SEC investigation is currently underway into whether the launch of BNB amounted to the sale of an unregistered security.

 The same day, a Reuters hit-piece was published claiming that Binance is “ a hub for hackers, fraudsters and drug traffickers ”.

 At a time when critics are feeling vindicated by the collapse of Luna and UST, the narrative that crypto is only for dirty money is an tempting one for mainstream media outlets to push. 

 However, Binance have published email transcripts showing a lack of willingness to cooperate on the part of the Reuters’ journalists who neglected to share the information necessary for the Binance team to investigate their claims.

 While the markets are down and bear-market apathy takes over, it’s clear that those who disapprove of crypto are making their moves.

 Ape season is well and truly over, and FUD season is in full swing. 

 But amongst all the doom and gloom, it’s important to remember that this is not our first rodeo… 

 Progress will not be linear. There will be hurdles; restrictions, scams and market crashes.

 However, the shared vision is key. 

 After all... no pain, no gain. 

 If you enjoy our work, please consider donating to our Gitcoin Grant .

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

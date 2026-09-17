# [H] Level Finance exploit: Yesterday, $1.1M in referral rewards were robbed from the BSC-based perps platform

## Summary
Severity: High
Target: Level Finance
Loss: $1,100,000
Published: 05/01/2023
Source: https://rekt.news/level-finance-rekt
Type: rekt-postmortem

## Details
## Level Finance - REKT

 Tuesday, May 2, 2023 Level Finance - BSC - REKT 

 read this article also in : zh 

 Level Finance got levelled. 

 Yesterday, $1.1M in referral rewards were robbed from the BSC-based perps platform. 

 The alarm was raised by definalist (whilst the attack was still ongoing) and confirmed two hours later by the Level Finance team.

 Luckily, the losses were contained to the project’s referral programme, with Treasury funds and LP both safe. 

 The hacker dumping LVL tokens for BNB initially crashed the price by 65%, though this has mostly recovered since.

 The attack was initially attempted over a week ago, but it seems nobody noticed.

 Could a warning have saved Level? 

 Credit: Peckshield , BlockSec 

 Level Finance’s LevelReferralControllerV2 contract contained a bug which allowed for repeated referral reward claims to be processed within the same epoch. 

 The exploiter prepared the attack by creating many referrals and using flash loans to make swaps, thereby increasing their reward tier.

 The claimMultiple function does not contain a check that the claim’s epoch is not being reused: 

 Exploiter's address: 0x70319d1c09e1373fc7b10403c852909e5b20a9d5 

 Example tx: 0xe1f25704… 

 LevelReferralControllerV2 contract: 0x977087422C008233615b572fBC3F209Ed300063a 

 The project was audited by Quantstamp and Obelisk , who both examined LevelReferralControllerV2 as part of the project’s Core contracts without spotting the bug. 

 UPDATE 09/05/2023 - Quantstamp contacted rekt.news stating that the vulnerability was introduced after their audit. They provided the following statement via DM: 

 The vulnerability was included in an upgrade done on April 18 ( bscscan.com/tx/0xe0a8e635f… ) that upgraded the proxy of LevelReferralControllerV2 ( bscscan.com/address/0x9770… ) to the vulnerable implementation ( bscscan.com/address/0x9f00… ).

 This code is different to the commit audited by Quantstamp as stated in the audit report ( certificate.quantstamp.com/full/level-fin… ). The source code for the vulnerable implementation in question is not committed in the official public repository of Level Finance in GitHub ( github.com/level-fi/level… ).

 In total, 214k LVL tokens were drained by the exploiter, who swapped them for 3,345 BNB, worth approximately $1.1M at the time of writing. The funds currently remain in the attacker’s address.

 The sell-off of tokens caused the LVL price to drop from $8.42 to a low of $2.93 (-65%), though this recovered substantially following the attack.

 As mentioned by BlockSec , the week that passed between the hacker’s first attempts and their eventual successful exploit demonstrates the potential of on-chain monitoring systems.

 When malicious contracts are created containing code designed to interact with DeFi protocols in unconventional ways, tools like Forta , Sentinel and Spotter are able to recognise the actions as suspicious, and alert teams accordingly.

 However, few incidents have so much warning. 

 DeFi protocols can go from SAFU to rekt from one block to the next. 

 Usually, though, an attack contract must be deployed before a hack can be executed. And even a few minutes' warning could be useful for more centralised protocols with the ability to pause contracts.

 If not, though, BlockSec’s own whitehat frontrunning system has intervened in a number of cases, saving funds and thwarting the efforts of hackers.

 Perhaps a future of on-chain sentinels protecting fully decentralised and self-executing code seems a long way off for now… 

 …but who knows what the future will bring? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

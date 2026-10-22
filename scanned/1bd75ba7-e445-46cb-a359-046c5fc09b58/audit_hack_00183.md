# [C] Nomad Bridge exploit: Nomad Bridge has been torn apart, with $190M of liquidity drained in a savage attack lasting two and a half hours

## Summary
Severity: Critical
Target: Nomad Bridge
Loss: $190,000,000
Published: 08/01/2022
Source: https://rekt.news/nomad-rekt
Type: rekt-postmortem

## Details
## Nomad Bridge - REKT

 Tuesday, August 2, 2022 Nomad Bridge - REKT 

 read this article also in : zh 

 The vultures had a busy night. 

 Nomad Bridge has been torn apart, with $190M of liquidity drained in a savage attack lasting two and a half hours.

 This is the 100th incident to make it onto the rekt.news leaderboard . 

 Staying true to DeFi principles, this hack was permissionless - anyone could join in . 

 Once the fatal blow had been struck, the news spread , and many began to fight over the scraps.

 Cross-chain bridges continue to be a weak point for DeFi and a juicy target for exploiters. And when they go, it's often a total collapse . 

 $190M... devoured. 

 The collateral damage from the unbacked assets is also severely affecting the chains that depended on Nomad. Moonbeam , EVMOS and Milkomeda have all taken a significant hit to their TVLs.

 This incident is distinct in its every-man-for-himself nature, but many who exploited the bug have declared themselves whitehats… Rekt is looking forward to seeing how much is eventually returned…

 Even so, with four of our leaderboard’s top 5 entries being cross-chain attacks, it gets ever more difficult to agree with Nomad’s slogan “ The future of cross-chain communication is optimistic ”. 

 But what started the feeding frenzy? 

 And how were so many able to continue picking the bones? 

 Credit: samczsun , Zellic.io 

 Following a routine upgrade in June, the bridge’s Replica contract was initialised with a fatal security flaw leading to the incident. The 0x00 address was set as a trusted root, meaning that all messages were read as valid by default.

 After a failed first attempt (costing $350k in gas), the original attacker’s exploit tx , which was copied by those that followed, was able to call the process() function directly, without having first ‘proved’ its validity.

 The process() function is responsible for the execution of all cross-chain messages and has an internal requirement ( line 185 ) to check the validity of the merkle root of all messages to be processed.

 However, the upgrade inadvertently caused transactions with a ‘messages’ value of 0 (invalid, according to legacy logic) to be read by default as 0x00 which was defined in the upgrade as a trusted root, passing the validation requirement as ‘proven’. 

 This meant any process() calls could be executed as valid. In fact, a more sophisticated exploiter could have written a contract to drain the whole bridge for themselves.

 Copycat attackers simply had to copy/paste the same process() function call via Etherscan, swapping out their address in place of the previous exploiter’s.

 The incident quickly proved to be a chaotic mixture of word-of-mouth crowdhacking, frantic whitehat activity and MEV-bot carnage. 

 For example, 🍉🍉🍉.eth managed to extract a total of $4M from the bridge, but fortunately claims to be acting as whitehat :

 However, other names stood out for the wrong reasons. There was a notable repeat offender in the Rari Capital (Arbitrum) exploiter from April’s article , who got away with almost $3M in stablecoins, which went straight into Tornado Cash.

 Of the multiple exploiters , the top three addresses (with 95M between them) are the following:

 0x56D8B635A7C88Fd1104D23d632AF40c1C3Aac4e3 ($47M)

 0xBF293D5138a2a1BA407B43672643434C43827179 ($40M)

 0xB5C55f76f90Cc528B2609109Ca14d8d84593590E ($8M)

 A full list of exploiter addresses is available here . 

 The project completed a Quantstamp audit in June, with issue QSP-19 foreshadowing a similar vulnerability:

 The auditor’s remarks that “ We believe the Nomad team has misunderstood the issue ” speak to a worrying attitude towards security that the project docs’ “ Long-Term Security ” plan appears to confirm:

 Concerns were also raised around the response time of the team facing a live and public exploit; the team’s official acknowledgement came three hours after the exploit began.

 The exploit was eventually halted by simply “ removing the Replica contract as owner ”, but after such a delay it was too late to save the funds.

 Blockchains may be closed systems, but alt L1 are only as strong as their weakest link. 

 The Harmony chain is still in disarray since its bridge lost $100M in late June, in an attack linked to the Lazarus Group .

 What will the future hold for the ecosystems affected by Nomad’s collapse? 

 So far, Moonbeam’s TVL has dropped from $300M to $135M, EVMOS’s from ~$7M to ~$3M, and Milkomeda’s from $31M to $20M.

 But crucially, the loss of confidence may prove to do far more damage than the missing $190M. 

 Building in an nascent, experimental industry is tough, and cross-chain infrastructure has many moving parts to secure. The damage done by bridge attacks are often the most painful, as they can contaminate a whole ecosystem, or more.

 But nomadic liquidity has no permanent home, users will always roam to new lands in search of the “next big thing”, and will continue to get stung whenever vigilance becomes stretched too thin. 

 With each of the 100 entries on the rekt.news leaderboard , the industry learns a harsh lesson, slowly growing stronger.

 But for now, DeFi still has plenty of easy prey… 

 …and scavengers continue to circle overhead. 

 Will it ever change? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

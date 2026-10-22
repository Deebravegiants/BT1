# [C] Curve, Vyper exploit: And Curve Finance returns to the leaderboard , 100x-ing their previous entry

## Summary
Severity: Critical
Target: Curve, Vyper
Loss: $69,300,000
Published: 07/30/2023
Source: https://rekt.news/curve-vyper-rekt
Type: rekt-postmortem

## Details
## Curve, Vyper - REKT

 Monday, July 31, 2023 Curve - Vyper - REKT 

 read this article also in : 

 Multiple protocols bit by the Vyper. 

 And Curve Finance returns to the leaderboard , 100x-ing their previous entry . 

 The total drained from the affected pools reached $69M ( nice ) and came from a number of protocols who use Curve for liquidity of their ETH-pegged assets: 

 JPEG’D lost $11.5M from the pETH/ETH pool

 Alchemix lost $20.5M from the alETH/ETH pool but were able to save $11.5M

 Metronome lost $1.6M from the msETH-ETH pool, with the attack tx frontrun by MEV bot 0xc0ffeebabe 

 And Curve itself lost $24.2M from the CRV/ETH pool, $5.4M of which was also frontrun by 0xc0ffeebabe, who quickly returned the funds.

 Smaller amounts were lost from dBridge ($25k from dormant LPs who hadn’t migrated affected) and BSC Curve-fork Ellipsis ($69k). 

 Peckshield raised the alarm on JPEG’d. Then when Alchemix was also hit , the DeFi community began to panic. 

 This was not just another iteration of the read-only reentrancy bug which has plagued the sector for the past months, despite what Curve initially, and dismissively, assumed .

 The tweet was deleted once it became clear that the problem ran deeper… 

 …were more pools at risk? 

 As the nature of the threat became clearer , Curve clarified , stating that the bug affected the alETH/msETH/pETH pools and that:

 Other pools are safe.

 Then Curve itself was hit when the CRV/ETH pool was drained for $24.3M. 

 Would this bloody Sunday ever end? 

 Credit: Vyper , Ancilia , Chaofan Shou , Tayvano 

 Initially, the hacks were thought to be due to the read-only reentrancy vulnerability which has damaged countless protocols over the last few months, most recently Conic Finance and EraLend . 

 However, the exploited contracts were not external projects using Curve pools as a price feed, but the Curve pools themselves… 

 The root cause was in fact a 0-day compiler bug in certain older versions of Vyper, the language Curve’s contracts are written in. 

 A misalignment of storage slots between two functions (add_liquidity and remove_liquidity) causes a malfunction in the nonreentrant guard . This allows the attacker/s to re-enter the transaction between these two functions in order to manipulated LP token prices and drain the pool.

 Any pool containing native ETH and written in versions 0.2.15, 0.2.16 and 0.3.0 was vulnerable. 

 The bug has been exploitable since 2021, and was patched (seemingly by accident, given no protective actions were taken) in version 0.3.1.

 Attacker’s addresses and attack transactions: 

 JPEG’D: 0x6ec21d1868743a44318c3c259a6d4953f9978538 

 Tx: 0xa84aa065… 

 Alchemix: 0xdce5d6b41c32f578f875efffc0d422c57a75d7d8 

 Tx: 0xb676d789… and 0x20d00acd… (whitehat tx)

 Metronome (whitehat frontrunner): 0xc0ffeebabe5d496b2dde509f9fa189c25cf29671 

 Tx: 0xc93eb238… 

 Curve: 0xB1C33b391C2569B737eC387E731E88589e8ec148 and 0xb752def3a1fded45d6c4b9f4a8f18e645b41b324 

 Tx: 0x2e7dc8b2… and 0x2e7dc8b2... 

 Despite not being able to find a workable exploit, Curve has advised users to withdraw from the Tricrypto pool on Arbitrum out of caution.

 Thankfully, although being from an older Vyper version, the stETH/ETH pool (>$400M TVL) is fine . 

 As the chaos was unfolding, whitehats rushed to save funds, but were repeatedly pipped to the post by hackers. 

 Some funds were saved, however, totalling $17M so far, with the Metronome funds likely to be returned (0xc0ffeebabe has already set 1000 ETH aside).

 But many were frustrated at the perceived irresponsible disclosure of the vulnerability (specifically the at-risk version numbers) while efforts were still on-going.

 BlockSec, who came under fire for publicly reaching out to Curve via Twitter, seem to have a clear conscience and defended their actions as having come after all exploitable pools were drained.

 Clout farming should take a back-seat when every second counts. 

 As banteg put it :

 you 👏 don't 👏 tweet 👏 live 👏 vulns 👏 before 👏 they 👏 are 👏 fully 👏 mitigated

 The losses have been heavy, but the fallout could be worse… 

 Many of the associated tokens took a beating: JPEG (initially -45%, since settled around -20%), pETH (initially -85%, then settled at around -40%), ALCX (down <10%), alETH (roughly -20%), CRV currently -15% but dropped to $0.60 at lowest point.

 And CRV is the one to watch… 

 The potential impact of such a large amount of CRV being dumped onto the open market (which the hacker still hasn’t done so far…) caused worries due to the highly-leveraged position of the protocol’s founder Michael Ergorov.

 In a fittingly degen manner, Ergorov has borrowed a total of $107.2M of stablecoins against $284M of CRV collateral across a variety of DeFi lending protocols. But with such a large quantity of CRV hanging in the balance, a liquidation cascade could cause much larger problems than yesterday’s hacks.

 Theories of perverse incentives aside, Ergorov does seem to be maneuvering but remains in a dicey position under pressure from rapidly increasing interest.

 For the sake of the whole sector let’s hope his good luck continues… 

 Some managed to profit from yesterday’s chaos, bots included, but are now being urged to do the right thing (by the alETH hacker no less, maybe hinting at some good news to come for Alchemix).

 While Curve has made clear that the other protocols were not at fault, it’s hard to know where the blame does ultimately lie. 

 Compiler-level vulnerabilities come as a chilling surprise to all involved. 

 Situations like these, which at times seemed to present an existential threat to a key piece of DeFi infrastructure, present an opportunity to break from business as usual and reprioritise.

 One of the most valuable innovations of our system is the transparency which allows us to dissect incidents like these in an open conversation, in stark contrast to TradFi. 

 The tools underlying our industry require just as much attention as the protocols they are used to build. With the majority of attention on Solidity, this vulnerability in Vyper snuck under the radar for years before being exploited.

 But the incentives are skewed… 

 Auditing projects can be good money, but generally takes for granted the stability of the underlying language. And with no token for VCs to dump on retail the base layer can often get forgotten about.

 With 59 contracts potentially affected, a similar bug in Solidity could see far more widespread damage. 

 This hack took a different approach to most. Not content with ripping off protocols for a million or so going after the same read-only reentrancy, the attacker/s targeted a deeper layer to find a way in.

 That kind of dedication and attention to detail sounds like a certain state-sponsored hacking group … 

 Or perhaps this time the bug was discovered by accident; it’s hard to imagine such a deeply buried vulnerability being painstakingly researched only to get frontrun on execution.

 Either way, this still offers an opportunity to change direction. 

 Given some of the larger protocols in the space have money to burn, and even more to lose , hiring in-house specialists to work on maintain and research could be money well spent.

 But while money remains attracted to our casino solely by the promise of moonshots, investment in the most basic level of infrastructure will likely continue to be lacking.

 Will we learn this time? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

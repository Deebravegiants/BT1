# [C] Mirror Protocol exploit: Two exploits hit Mirror Protocol, and the larger of the two wasn’t even noticed at first

## Summary
Severity: Critical
Target: Mirror Protocol
Loss: $92,000,000
Published: 10/08/2021
Source: https://rekt.news/mirror-rekt
Type: rekt-postmortem

## Details
## Mirror Protocol - REKT

 Tuesday, May 31, 2022 Mirror - Terra - REKT 2 

 read this article also in : zh 

 Mirror mirror on the wall… 
 $90 million stolen, but that’s not all. 

 Two exploits hit Mirror Protocol, and the larger of the two wasn’t even noticed at first. 

 When the Ronin Bridge hack was announced, we were all shocked to hear the funds were missing for a week before the alarm was raised.

 It took Mirror Protocol seven months, to spot the loss, and when they did finally notice, they didn’t publicly announce anything.

 And then, 232 days later, they were hit again.

 The day after the first loss was revealed, another $2M was taken.

 How embarrassing. 

 Mirror devs need to take a long hard look in the… 

 Credit: FatManTerra , pedroexplore1 

 The first exploit, executed on the 8th of October 2021, involved repeatedly unlocking collateral deposited against short positions on Mirror Protocol.

 The lock contract did not contain a duplicate call check for withdrawals, allowing the attacker to drain funds deposited by other users by calling unlock_position_funds for their own position ID multiple times.

 Attack transaction: 08DD2B70… 

 For a step-by-step analysis see this BlockSec blog post . 

 Despite the vulnerability remaining live, no followup attack was made; the balance of the lock contract never rose high enough to exploit again without alerting the protocol’s userbase.

 As FatManTerra pointed out on Twitter:

 ”All of this went completely unnoticed by TFL and the Mirror team & community.”

 On the 14th of May, the vulnerability was finally, and quietly, patched with no mention of the bug nor the $90M loss it had produced just seven months earlier.

 Suspicions were raised when users on the forum began to look into the bugfix, provoking a discussion as to why the devs had “smuggled” in the fix without an announcement.

 Eventually, the details were published by FatMan on 27th May.

 However, the day after the news of the original incident broke, the latest exploit was spotted.

 Mirror Hack Two: LUNA Switcheroo 

 Source: Mirroruser , Blockpane , FatManTerra 

 “Mirroruser” first posted the details to the Mirror forum, alerting the community to the loss of funds.

 Due to the same mispricing of LUNC that led to the Anchor exploit , LUNC was assigned the value of LUNA 2.0 on the new chain, at the time ~5 USTC (approx. ~$0.10).

 The issue was down to Luna Classic validators running an out-of-date oracle , which hadn’t been updated for the legacy chain.

 This meant that users could buy cheap LUNC, deposit as collateral, and take advantage of the overvaluation to drain Mirror’s pools. The protocol’s mBTC, mETH, mDOT and mGLXY were drained, totalling ~$2M for the attacker.

 After news of the exploit over the weekend, the oracle was successfully fixed, but the problems didn't stop there.

 All mAssets (Mirror-wrapped stocks) were still for the taking, unable to be traded until markets opened following the long-weekend. The worry was that the previously stolen funds would be used to snap up the remaining, vastly-undervalued mAssets.

 However, with just minutes to spare before markets opened on Tuesday, the stolen funds were disabled for use as collateral, saving what remained of the protocol.

 The fact that a $90M exploit went unnoticed by users (and probably the devs), is symptomatic of the recklessness associated with the failings around the Terra ecosystem. 

 The simplicity of the vulnerabilities seems out of place when compared with the damage that has been done. Firstly, $90M was lost to a basic logic bug, and then, the rushed fork led to the oversight of a very foreseeable oracle issue.

 Even in the face of these failures, Luna 2.0 is pumping and, despite having lost billions of dollars of other people's money, Do Kwon remains as arrogant as ever. 

 In his rush to repair his reputation, Kwon is taking advantage of all those who are stuck fighting sunk-costs; the developers who invested their time, and retail, who invested their savings.

 DeFi today feels like it has lost a sense of purpose. Our reputation is damaged, and even the keenest users have less confidence. 

 We may have advanced our methods of wealth distribution, but our moral compass clearly still needs an update.

 Imagine our industry without all the ego… How much of this damage could have been prevented? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

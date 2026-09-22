# [H] Onyx Protocol exploit: Onyx Protocol , a Compound Finance fork, lost $2.1M on Tuesday to a high-profile, well-known vulnerability

## Summary
Severity: High
Target: Onyx Protocol
Loss: $2,100,000
Published: 11/01/2023
Source: https://rekt.news/onyx-protocol-rekt
Type: rekt-postmortem

## Details
## Onyx Protocol - REKT

 Thursday, November 2, 2023 Onyx Protocol - Fork - REKT 

 read this article also in : 

 Another total fork-up. 

 Onyx Protocol , a Compound Finance fork, lost $2.1M on Tuesday to a high-profile, well-known vulnerability. 

 The exact same attack vector has hit two other forks, Hundred Finance and Midas Capital ( themselves both repeat leaderboard entrants ), already this year, tipping the total lost to this bug over the $10M mark.

 Peckshield, as ever, warned Onyx to “ take a look ”. However, no official response came for almost three hours, when a team member acknowledged the loss.

 In the meanwhile, and while TG mods were urging users “ Please don’t fud ” the protocol was hit by a repeat attack , though for substantially less profit ($~62k).

 Many protocols have fallen victim to repeated exploits of identical vulnerabilities over the course of the year, with read-only reentrancy also claiming multiple victims including Conic , Sturdy , EraLend and Midas .

 Are the devs paying attention? 

 Credit: Peckshield , BlockSec 

 The exploit was made possible due to a known vulnerability of Compound v2 code. Under certain conditions, a rounding error allows an attacker to manipulate empty markets in order to drain liquidity from across the protocol. 

 In Onyx’ case, governance had recently voted through Proposal 22 to add a lending market for memecoin PEPE to the protocol.

 The ‘empty market attack’ involves taking a flash loan which is swapped, in this case, for PEPE. Then, by minting a small number of shares (oPEPE) and donating a large amount of PEPE to the pool, vastly inflating the price of oPEPE for use as collateral on Onyx.

 Other assets can then be borrowed against the overvalued oPEPE, draining the protocol’s liquidity. The rounding error is then exploited to withdraw the donated funds, and the flash loan is repaid.

 Exploiter address: 0x085bdff2c522e8637d4154039db8746bb8642bff 

 Attack tx: 0xf7c21600… 

 Repeat exploiter address: 0x5083956303a145f70ba9f3d80c5e6cb5ac842706 

 Repeat-attack tx: 0x27a3788d… 

 The 1164 ETH ($2.1M) of profits were sent on to an intermediary address before 1140 ETH were deposited into Tornado Cash. 

 The remaining 24 ETH were sent to on-chain panhandlers, prompting a follow-up stream of input data messages to the hacker’s address, begging for further scraps. 

 Onyx Protocol was audited by Certik , however the viability of this vulnerability is ultimately determined by the conditions within the individual market, rather than the codebase in itself.

 Empty markets in Comp v2 code are a known issue; the launch of new markets should be treated especially carefully by project teams. 

 The discussion following the (second) Hundred Finance hack references Hexagate’s recommendations for launching potentially vulnerable markets (“ markets with low total supply and a non-zero collateral factor (CF) ”):

 we recommend any Compound V2 fork, when launching new markets to mint some cTokens and burn them to make sure the total supply never goes to zero. When the total supply goes to zero, the protocol becomes vulnerable and this strategy mitigates this situation.

 That means that when listing a new collateral token, first set its collateral factor to zero, set in the Comptroller, mint some cTokens, burn them and then change the collateral factor to the desired factor.

 Compound itself has many eyes scouring all governance proposals, though the occasional blunder does seem to slip through … 

 But with just 11 wallets voting on Proposal 22 ( and over 97% of votes coming from a single address ), perhaps Onyx doesn’t have the same level of community vigilance over its lending markets.

 For teams working with forks, devs must be sure to stay on top of the security landscape, to avoid getting rekt by replicated vulnerabilities. 

 Blackhats are certainly keeping up-to-date. 

 Onyx’ proposed compensation plan intends to refund victims by selling native tokens from the treasury, while DAO contributors' salaries will be paused until further notice. 

 While superficially sounding like a fair and selfless way to make users whole, the plan has the potential to trigger a death sprial on XCN, whilst the team’s incentives grow increasingly misaligned…

 What could go wrong? 
 
## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

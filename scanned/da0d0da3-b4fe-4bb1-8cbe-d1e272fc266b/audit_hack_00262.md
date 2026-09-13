# [H] TempleDAO exploit: TempleDAO’s STAX, was hacked yesterday for approximately $2.3M worth of LP tokens

## Summary
Severity: High
Target: TempleDAO
Loss: $2,300,000
Published: 10/11/2022
Source: https://rekt.news/templedao-rekt
Type: rekt-postmortem

## Details
## TempleDAO - REKT

 Wednesday, October 12, 2022 TempleDAO - REKT 

 read this article also in : zh 

 TempleDAO’s STAX, was hacked yesterday for approximately $2.3M worth of LP tokens. 

 TempleDAO launched as one of many OHM-forks in the run-up to last year’s market top, before pivoting to stablecoin farm when the Olympus model crumbled.

 Temple’s current focus is on yield for FRAX3CRV via Convex, and STAX forms part of their “ flywheel system ” as “ a reward boosting liquidity layer for the FRAX/TEMPLE gauge ”.

 Despite initially establishing a cult-like following, the devotion of their users seems to be waning. 

 The day before the exploit, DCF GOD responded to a TempleDAO community vibe check:

 ”After a year of it, I’m low on hope”

 Now that users have lost all hope, who still has faith in Temple DAO? 

 The alarm was raised by Spreek approximately an hour after the exploit, which was later confirmed by STAX . Although the damage done is unlikely to pose an existential threat to the wider TempleDAO protocol, the details of the exploit make for painful reading.

 How did the devs make such a simple oversight when they published the contract in June? 

 And why did it take so long to be exploited? 

 Credit: FrankResearcher , BlockSec 

 This hack was worryingly simple. 

 The StaxLPStaking contract’s migrateStake() function did not contain any checks that the oldStaking parameter was valid.

 This meant that anyone could create a contract with the same oldStaking parameter, specifying an arbitrary deposit amount and address to which the funds could be sent.

 The resulting ~320k Stax Frax/Temple LP tokens were then swapped for ETH inside the attacker’s contract .

 Attacker’s address: 0x9c9fb3100a2a521985f0c47de3b4598dafd25b01 

 Attack tx: 0x8c3f442f… 

 The exploiter’s address was funded via Binance shortly before the attack, and the stolen funds were forwarded to another address ( 0x2b63d4a3b2db8acbb2671ea7b16993077f1db5a0 ) where they remain.

 $2M is a relatively small amount compared to the TVL of TempleDAO, (~$57M according to DeFiLlama ). 

 STAX have assured that ” Remediations will be made for all affected users. ”

 Arguably, the greatest damage done will be to the project’s reputation, after allowing such a basic error to make it to production. 

 TempleDAO have pointed out that their Temple Core Vaults are secure and share no common code with STAX. However, after such a simple oversight…

 Can Temple users keep the faith? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

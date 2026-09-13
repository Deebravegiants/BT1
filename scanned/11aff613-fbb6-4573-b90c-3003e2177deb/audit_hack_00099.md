# [H] EraLend exploit: Yesterday, EraLend , a lending platform on zkSync Era, lost $3.4M to the rampant read-only reentrancy bug plaguing protocols across the cryptosphere

## Summary
Severity: High
Target: EraLend
Loss: $3,400,000
Published: 07/25/2023
Source: https://rekt.news/eralend-rekt
Type: rekt-postmortem

## Details
## EraLend - REKT

 Wednesday, July 26, 2023 EraLend - zksync - REKT 

 read this article also in : 

 One more added to the list. 

 Yesterday, EraLend , a lending platform on zkSync Era, lost $3.4M to the rampant read-only reentrancy bug plaguing protocols across the cryptosphere. 

 The alarm was raised and the losses stacked up . Syncswap was keen to reassure their users that they were not at risk, though recommended pulling LP tokens from EraLend as a precaution. In the end, only USDC deposits on EraLend were affected.

 This is the second leaderboard entry to come from zkSync, after Merlin DEX ’s $1.8M rugpull in April.

 With hack szn hotting up, where will be hit next? 

 Credit: Spreekaway , Peckshield 

 Read-only reentrancy is nothing new, with last Friday’s attack on Conic Finance the latest in a long line of projects rekt by the issue. 

 In EraLend’s case, the attacker was able to exploit the vulnerability via a callback when burning LP tokens. 

 in the syncswap LP tokens, one can burn, then callback before update_reserves is called. so the oracle uses an incorrect reserves value to calculate the price, resulting in an inflating oracle price.

 The buggy code was recycled from SyncSwap, but improperly implemented. Astonishingly, the code even contained the comment pointing out the potentially risky routine, which was apparently ignored:

 Note reserves are not updated at this point to allow read the old values.

 But comments are not effective reentrancy protection . 

 Exploiter address: 0xf1D076c9Be4533086f967e14EE6aFf204D5ECE7a 

 Example attack txs: 0x7ac4da1e… , 0x99efebac… 

 Of the $3.4M lost from EraLend, Hacken puts the attacker profits at around $2.66M and traced funds to addresses on ETH, ARB and OP. 

 BlockSec tweeted a warning to other projects that may be using the same code: 

 Alert! All projects that rely on the following Syncswap code need to be vigilant.

 But given the prevalence of this attack type over the last months, why haven’t all devs already double (or triple) checked by now? 

 Peckshield, who audited EraLend (then Nexon Finance) in March, washed their hands of responsibility. The audit apparently “ assumes a trusted price oracle ”, simplifying their job by simply ignoring one of the trickiest and most exploitable parts of many DeFi protocols.

 As noted by ChainSecurity’s Matthias Egli at EthCC last week, the losses from this string of hacks is far lower than the potential losses from far larger protocols that had been vulnerable before the vector was discovered last year.

 But that silver lining likely doesn’t make much difference to EraLend users. 

 How long until this bug strikes again? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

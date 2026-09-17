# [M] Autoshark exploit: Before we’ve even caught up with the weekend's affairs, another one is dead in the water

## Summary
Severity: Medium
Target: Autoshark
Loss: $745,000
Published: 05/24/2021
Source: https://rekt.news/autoshark-rekt
Type: rekt-postmortem

## Details
## Autoshark - REKT

 Tuesday, May 25, 2021 Autoshark - REKT 

 read this article also in : zh 

 We’re going to need a bigger team. 

 Before we’ve even caught up with the weekend's affairs, another one is dead in the water.

 Autoshark hacked, and now they swim with the fishes, although the damage was small: only ~$745k profit.

 Perhaps the hacker who donated $100k DAI to the rekt.news treasury didn’t like to see Autoshark fishing for promotion in the replies. 

 8 hours later, Autoshark fell victim to the same exploit as the PancakeBunny hack. 

 credit : watchpug 

 1: Add a small sum of deposit to the SHARK-BNB Vault (with this transaction).

 2: Borrow 100K BNB of flash loan from PancakeSwap.

 3: Swap 50K BNB into SHARK token and send them alongside the rest 50K BNB to the SharkMinter contract. (this is important! this is the key to the hack.)

 4: Call getReward with the deposit of SHARK-BNB Vault from the first step.

 5: With the huge amount of SHARK token and WBNB in the wallet balance of the minter contract (sent by the hacker at step 3), it returned an extremely large amount of profit. As a result, the system minted 100M SHARK as a reward to the hacker. (plus 15M for Dev and 20M for Referrer)

 6: Sold SHARK token for 102K WBNB, repaid flash loans, taken out 2.2K WBNB.

 The 50K BNB and 50K BNB worth of SHARK token sent to the contract’s wallet at step 3 made the contract believe the profit was very high. 

 The result: 100M (plus 15M for Dev and 20M for Referrer) of Shark token minted and dumped. 

 Transaction Details on BscScan. 

 The tides have turned on BSC, and they’re now in damage prevention mode. 

 Any new DeFi ecosystem will have to pass through this phase, but poorly copied code won’t take them far.

 There’s plenty of audit firms who are willing to ignore mistakes in low quality code, and we must consider their motives.

 We’re watching you. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

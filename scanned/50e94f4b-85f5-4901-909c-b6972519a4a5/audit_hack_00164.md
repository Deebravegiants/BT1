# [M] Merlin Labs exploit: The PancakeBunny attack pulled the rabbit out of the hat, now a surprisingly similar string of attacks emerges from Binance Smart Chain

## Summary
Severity: Medium
Target: Merlin Labs
Loss: $680,000
Published: 05/26/2021
Source: https://rekt.news/merlinlabs-rekt
Type: rekt-postmortem

## Details
## Merlin Labs - REKT

 Wednesday, May 26, 2021 Merlin Labs - REKT 

 read this article also in : zh 

 Security looser than a wizard's sleeve. 
 The PancakeBunny attack pulled the rabbit out of the hat, now a surprisingly similar string of attacks emerges from Binance Smart Chain .

 $680,000 taken from Merlin Lab . 

 We have to set ourselves some standards here at rekt.news - generally we won’t report on hacks concerning less than $1M, but when there’s something worth saying we’ll say it.

 The same technique has been used three times in one week. 

 BSC developers must try harder. 

 Credit: watchpug 

 On May 26, 2021, 03:59:05 AM +UTC, less than 48 hrs after the Autoshark hack. Merlin Lab, (another fork of PancakeBunny), was attacked in a similar fashion to the Bunny and the Autoshark hack. 

 As a result, the hacker was able to remove ~240 ETH (~680K USD).

 Transaction Details on BscScan. 

 1: Add a small sum of deposit to the LINK-BNB Vault (with this transaction).

 2: Send 180 CAKE to the LINK-BNB Vault contract. (This is the key that leads to the hack.)

 3: Call getReward with the deposit of LINK-BNB Vault from the first step.

 4: With the large amount of CAKE token in the wallet balance of the vault contract (sent by the hacker in step 2), it returns a large amount of profit. As a result, the system minted 100 MERL as a reward to the hacker.

 5: Repeat 36 times. Receive 49K of MERL token in total.

 6: Swapped MERLIN token into 240 ETH and transferred out of BSC using Anyswap.

 The hacker used the wallet balance of CAKE as the profit (performanceFee) which can be easily tampered with by just sending the CAKE token to the vault contract. 

 We don’t document these attacks to help the hackers, although sometimes they might thank us for our work . 

 Each attack provides a lesson for the protocols that remain.

 If these lessons are ignored, meaning users' funds are lost, then what does that say about the founders and the auditors?

 Merlin Labs was audited by Hacken on May 15th, just 11 days before this exploit. 

 Now they both take a spot at the bottom of our leaderboard .

 Must try harder. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Jimbo's Protocol exploit: Jimbo’s Protocol was hit with a flash loan attack in the early hours of Sunday, losing $7.5M

## Summary
Severity: High
Target: Jimbo's Protocol
Loss: $7,500,000
Published: 05/28/2023
Source: https://rekt.news/jimbo-rekt
Type: rekt-postmortem

## Details
## Jimbo's Protocol - REKT

 Monday, May 29, 2023 Jimbo's Protocol - Arbitrum - REKT 

 read this article also in : 

 The exploits are stacking up on Arbitrum. 

 Jimbo’s Protocol was hit with a flash loan attack in the early hours of Sunday, losing $7.5M. 

 The project, which aims to create a semi-stablecoin via rebalancing (OHM flashbacks, anybody?), had just relaunched. Its v2 was an attempt to fix a buggy v1 which fell apart on launch earlier this month.

 As UltraXBT put it:

 Kinda sus $JIMBO v1 failed because it was way too complicated and now 1 week later they have decided to launch a v2 with even more complexity by adding leverage

 Very dope if they succeed and rooting for them but this is a lot of moving parts for a defi protocol

 After just three days of the v2 protocol, the alarm was raised . 

 An acknowledgement eventually came from the team, almost six hours after being alerted via Twitter.

 Wake up Jimbo. 

 This is the sixth incident we’ve covered on Arbitrum this year, with dForce Network , Dexible , Hope Finance , Deus DAO (no. 3) and Swaprum all taking losses since the start of 2023.

 Are we seeing a repeat of Spring 2021’s carnage on BSC? 

 Credit: Peckshield , Numen Cyber 

 The hack was due to a lack of slippage control in the shift() function of the JimboController contract . 

 The attacker took a flashloan of 10k ETH and used the funds to buy JIMBO, heavily increasing the token’s price. Then, by depositing some of the overvalued JIMBO into the JimboController, a rebalance was triggered via shift(), transferring the contract’s WETH back into the pool.

 The attacker was then able to sell the remaining JIMBO back into the pool, draining all WETH liquidity and crashing the price of JIMBO.

 Attacker’s address: 0x102be4bccc2696c35fd5f5bfe54c1dfba416a741 

 Location of stolen funds (ETH): 0x5f3591e2921d5c9291f5b224e909ab978a22ba7e 

 Attack tx: 0x3c6e053f… 

 Over 4000k ETH (~$7.5M) were bridged back to Ethereum, where they remain in the above address.

 Jimbo has reached out to the hacker on-chain, offering a 10% bounty for the return of funds. 

 They seem confident in getting a result, trying to push the hacker into responding with an ultimatum :

 We are already working with multiple security researchers and on-chain analysts who helped with both the Euler Finance and Sentiment exploits.

 We will start working with law enforcement agencies tomorrow by 4PM UTC if this isn’t sorted out by then.

 But unless the attacker responds, it looks like Jimbo is stuck in limbo. 

 Will we see a v3? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

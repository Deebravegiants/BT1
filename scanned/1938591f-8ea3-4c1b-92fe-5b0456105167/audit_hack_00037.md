# [C] bEarn exploit: Binance Smart Chain provides the easiest prey for the anonymous apex predator

## Summary
Severity: Critical
Target: bEarn
Loss: $18,000,000
Published: 05/17/2021
Source: https://rekt.news/bearn-rekt
Type: rekt-postmortem

## Details
## bEarn - REKT

 Monday, May 17, 2021 bEarn - REKT 

 read this article also in : zh 

 Every weekend another one falls. 
 Binance Smart Chain provides the easiest prey for the anonymous apex predator.

 Hard-hearted hackers are fast to feast on copied code from developers keen to cut corners.

 Another week finished and another protocol with it. 

 $18 million gone from bEarnFi. 

 The following is taken from the Peckshield and bEarn analysis .

 Starting at 10:36:20 AM +UTC, May 16, 2021, BearnFi’s BvaultsBank contract was exploited and approximately $18M funds were drained from the pool. 

 The incident was made possible due to a bug in the internal withdraw logic, which inconsistently read the same input amount, but with different asset denominations between the BvaultsBank and the associated strategy BvaultsStrategy.

 The BvaultsBank's withdraw logic assumes the withdrawn amount is denominated in BUSD while the BvaultsStrategy's withdraw logic assumes the withdrawn amount is denominated in ibBUSD.

 However, ibBUSD is an interest-bearing token and is more expensive than BUSD . 

 1: Borrow a flashloan from CREAM with 7,804,239.111784605253208456 BUSD, which is returned at the last step with necessary fee to cover the flash loan cost.

 2: Deposit the borrowed funds into BvaultsBank, which are immediately sent to the associated BvaultsStrategy strategy, then to Alpaca Vault for yield. Due to the above deposit, the Alpaca Vault mints 7,598,066.589501626344403426 ibBUSD back to BvaultsStrategy.

 3: Farm with the received 7,598,066.589501626344403426 ibBUSD via the Alpaca FairLaunch.

 4: Withdraws the 7,804,239.111784605253208533 BUSD from BvaultsBank, which is interpreted as withdrawing 7,804,239.111784605253208533 ibBUSD, the equivalent of 8,016,006.09792806917101481 BUSD.

 5: In the next round, the user still deposits 7,804,239.111784605253208533 BUSD into BvaultsBank, cascadingly to BvaultsStrategy. But with the previous leftover from the last round, BvaultsStrategy credits the user with 8,016,006.09792806917101481 BUSD, which is used for yield again via Alpaca.

 6: Repeat the above steps to continue accumulating the credit and finally exits by draining the pool.

 7: Return the flash loan with 7,806,580.383518140634784418 BUSD.

 The attacker’s funds from the above exploitations were initially held in this wallet: 47f3 .

 Another week begins. Has the hacker returned richer to their day job, or do they attack on weekends as they expect less attention? 

 The boom in BSC code copies has created a wealth of new opportunities for any developer who seeks to exploit protocols.
As we watch the rapid rise and fall of TVL on BSC, it becomes even more apparent that time is the most valuable audit of all.

 Longevity suggests security, and vice versa.

 How long until the next rekt comes along? 

 Photography by Ray Metzker 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

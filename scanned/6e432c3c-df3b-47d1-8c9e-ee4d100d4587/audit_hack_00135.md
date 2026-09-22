# [H] Inverse Finance exploit: $1.2M to the anonymous attacker, and $5.8M lost overall

## Summary
Severity: High
Target: Inverse Finance
Loss: $5,800,000
Published: 06/16/2022
Source: https://rekt.news/inverse-rekt2
Type: rekt-postmortem

## Details
## Inverse Finance - REKT 2

 Thursday, June 16, 2022 Inverse Finance - REKT 

 read this article also in : zh 

 Flipped again. 

 $1.2M to the anonymous attacker, and $5.8M lost overall.

 This is the second leaderboard entry for Inverse Finance , who also lost $15M to a price manipulation attack just two months ago.

 Now, another oracle manipulation has hit the protocol’s DOLA lending market, which, according to the Risk DAO dashboard, now has $10.63M of bad debt. 

 Peckshield jumped at the chance to tweet about the exploit, but deleted their announcement after being publicly reprimanded for disclosing the vulnerability while funds were still at risk.

 Inverse Finance announced the incident, stating that:

 ”no user funds were taken or were at risk.”

 Credit: Peckshield 

 The attacker was able to manipulate the pricing of yvcrv3Crypto used as collateral. The Inverse oracle “ misuses the balances of assets in the pool to directly calculate the LP token price. ”

 By using the flash loaned WBTC to make large swaps through the underlying pool, the balance of assets was manipulated before and after borrowing, allowing the exploiter to withdraw an inflated amount of DOLA.

 1: Flashloan 27,000 WBTC via AAVE

 2: Deposit 225 WBTC to crv3crypto with 5,375 crv3crypto minted

 3: Deposit 5,375 crv3crypto to y Curve-3Crypto with 4,906 yvCurve-3Crypto minted

 4: Deposit 4,906 yvCurve-3Crypto to Inverse Finance as collateral

 5: Swap 26,775 WBTC to 75,403,376 USDT to manipulate the collateral price

 6: Borrow 10,133,949 DOLA, which is extremely more than normal

 7: Reverse swap 75,403,376 USDT to 26,626 WBTC

 8: Swap 10,133,949 DOLA to 9,881,355 3Crv

 9: Remove 9,881,355 3Cry to get 10,099,976 USDT

 10: Swap 10,000,000 USDT to 451 WBTC

 11: Repay flashloan

 Funds were then withdrawn from the contract and swapped to ETH, 1000 of which have been deposited into Tornado Cash, and 68 remain in the address.

 Exploiter’s address, funded via Tornado Cash 2 mins before exploit: 0x7b792e49f640676b3706d666075e903b3a4deec6 

 Exploit contract: 0xf508c58ce37ce40a40997c715075172691f92e2d 

 Exploit tx: 0x958236… 

 Withdrawing 100k USDT from the contract: 0x3d2f86… 

 Withdrawing 53 WBTC ($1.1M) from the contract: 0x9959f8… 

 Peckshield further confused matters after the attack by suggesting that the malicious tx had in fact been executed by a front-running bot, who had sniped the tx before the exploiter.

 Others disagreed with the claim, and as the address was funded, and then the loot laundered, via Tornado Cash so quickly. It seems unlikely that we’re dealing with an accidental attack, however, it’s not hard to imagine such a turn of events happening in the future.

 After two hacks in such quick succession, and with bad debt making up over half of the protocol’s 20M TVL, will Inverse be able to survive this crypto winter?

 If you enjoy our work, please consider donating to our Gitcoin Grant .

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

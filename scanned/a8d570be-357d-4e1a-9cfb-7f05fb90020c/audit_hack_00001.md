# [H] Eleven Finance exploit: Eleven.finance , a yield aggregator on Binance Smart Chain (BSC) and Polygon (MATIC) was exploited for a total of $4.5M

## Summary
Severity: High
Target: Eleven Finance
Loss: $4,500,000
Published: 06/22/2021
Source: https://rekt.news/11-rekt
Type: rekt-postmortem

## Details
## Eleven Finance - REKT

 Wednesday, June 23, 2021 Eleven Finance - BSC - REKT 

 read this article also in : zh 

 This one almost struck a nerve . 

 Eleven.finance , a yield aggregator on Binance Smart Chain (BSC) and Polygon (MATIC) was exploited for a total of $4.5M.

 Some feared that it was the much larger Nerve Finance who was under attack, but it was in fact the NRV vault of Eleven Finance.

 There’s no rest for the wicked - who would attack at such an ungodly hour? 

 Credit: 0xdeadf4ce 

 Transaction details here. 

 The root cause was a function called emergencyBurn() in the intermediary vault used to track anySwap / Nerve-bridged assets nrvBTC, nrvETH and nrvFUSDT in the Eleven “MasterMind” farming contract. 

 The attacker first took a Flashloan of each asset’s underlying token balance in the “MasterMind” contract (Binance-pegged BTC, ETH and USDT) to convert these into nrvBTC, nrvETH and nrvFUSDT respectively.

 Nerve 3Pool and PancakeSwap BUSD - NRV liquidity provider positions were also affected. 

 A vulnerable function emergencyBurn() in the intermediate vault contract allowed the attacker to withdraw the deposited balance without having the withdrawal being accounted for internally.

 As a result the attacker was able to not only remove his own deposit but the full balance of the same amount that had been in the vault before as well. 

 The attacker used the Nerve bridge to transfer out 2,293 ETH in proceeds to the address 0xdb2d590aCe7cAe51DF1fB3312738038Ec032Bf33.

 Steps 

 1: borrow underlying assets from PancakeSwap (Flash Swap)

 2: convert amount (mint) to Nerve asset

 3: deposit Nerve asset to “MasterMind” through intermediate vault

 4: call emergencyBurn() on intermediate vault, transferring an amount equal to the previously deposited amount (equal to vault balance before attack) to the attacker

 5: proceed with a regular withdrawal, transferring the previously deposited asset balance back to the attacker

 Funds lost 

 30.75 BTCB
for ~$1.05M from nrvBTC

 286 ETH
for ~$561K from nrvETH

 2.241M BUSD
for ~$2.241M from NRV 3Pool LP

 0.647M BUSD
for $647K from NRV - BUSD LP

 $4.5 million gone, entering at position 27 on the ever expanding rekt leaderboard. 

 Peckshield blamed this on a “dumb logic issue”; a shockingly simple way to lose over four million dollars.

 Fear and greed is on the rise , will we see more attacks now that honest work is harder to find?

 If you enjoy our work, please donate to our Gitcoin grant. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

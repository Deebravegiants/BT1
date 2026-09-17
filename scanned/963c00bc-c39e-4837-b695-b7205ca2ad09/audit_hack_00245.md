# [C] Spartan Protocol exploit: A flaw in the code allowed an attacker to drain the SPARTA/WBNB liquidity pool, earning themselves $30.5 million and the 6th position on the rekt lead

## Summary
Severity: Critical
Target: Spartan Protocol
Loss: $30,500,000
Published: 05/02/2021
Source: https://rekt.news/spartan-rekt
Type: rekt-postmortem

## Details
## Spartan Protocol - REKT

 Sunday, May 2, 2021 Spartan Protocol - REKT 

 read this article also in : zh 

 Sparta has fallen. 

 A flaw in the code allowed an attacker to drain the SPARTA/WBNB liquidity pool, earning themselves $30.5 million and the 6th position on the rekt leaderboard as a result.

 The attacker took advantage of a flawed logic used to calculate liquidity shares when users burned their LP tokens in order to withdraw funds.

 A flash loan was used to inflate the balance of the pool before burning the same amount of pool tokens, allowing them to claim a much larger amount of underlying assets.

 The following details are taken from the Peckshield root cause analysis.

- 
 A flash loan was taken for 10K WBNB, to be returned at the last step with 260 WBNB as the flash loan fee; 

- 
 Swap WBNB to SPARTA five times through the exploited Spartan pool, with each time swapping in 1,913.172376149853767216 WBNB to get 621,865.037751148871481851 SPARTA,

 555,430.671213257613862228 SPARTA,

 499,085.759047974016386321 SPARTA,

 450,888.746328171070956525 SPARTA,

 and 409,342.991760515634291439 SPARTA respectively.

- 
 The resulting total 2,536,613.206101067206978364 SPARTA, plus 11,853.332738790033677468 WBNB, are then added into the pool, minting 933,350.959891510782264802 pool token (SPT1-WBNB);

- 
 Swap WBNB to SPARTA ten times through the same pool , with each time swapping in 1,674.025829131122046314 WBNB to get 336,553.226646584413691711 SPARTA,

 316,580.407937459884368081 SPARTA,

 298,333.47575083824346321 SPARTA,

 281,619.23694472865873995 SPARTA,

 266,270.782888292437349121 SPARTA,

 252,143.313661963544185874 SPARTA,

 239,110.715943602161587616 SPARTA,

 227,062.743086833745362627 SPARTA,

 215,902.679301559370989883 SPARTA,

 and 205,545.395265586231012643 SPARTA respectively,

 resulting in a total of 2,639,121.977427448690750716 SPARTA.

- 
 Inflate the asset balance in the pool by transferring into the pool 21,632.147355962694186481 WBNB and all SPARTA from the above step 3, i.e., 2,639,121.977427448690750716 SPARTA.

- 
 Burn the 933,350.959891510782264802 pool tokens obtained from step 2 to withdraw the liquidity. Since the pool’s asset balance is inflated, the burn operation leads to 2,538,199.153113548855179986 SPARTA and 20,694.059368262615067224 WBNB.

 Note that step 2 only deposits 11,853.332738790033677468 WBNB, leading to the profit of about 9K WBNB.

- 
 Add the liquidity into the pool with the added assets in step 4 with 1,414,010.159908048805295494 pool token, which is immediately burned to obtain 2,643,882.074112804607308497 SPARTA and 21,555.69728926154636986 WBNB.

- 
 Repeat the above steps to continue draining funds from the pool. 

- 
 Return the flash loan with 100,260 WBNB. 

 The vulnerability stems from the fact that the liquidity share calculation calcLiquidityShare() is querying the current balance which can then be inflated for manipulation. A correct calculation needs to make use of cached balance in baseAmountPooled/tokenAmountPooled.

 Most of the attacker’s funds from the above exploitations are currently held in this wallet: 0x3b6e .

- 30.7k WBNB ($18.9M)

- 4.6M SPARTA ($7.8M at the time of hack)

- 1.3M BUSD-T ($1.3)

- 23.2 BTCB ($1.3M)

- 924k BUSD ($0.9M)

 The attacker used 1inch (to swap all tokens to BTCB or BETH), Spartan (to dump SPARTA), Nerve (to swap BTCB and BETH to Anyswap versions). In this way they were eventually able to withdraw part of the profit through Anyswap.

 Due to slippage, the profit decreased by a third:

- 219.5 BTC ($12.4M)

- 3311 ETH ($9.7M)

 Credit igor igamberdiev 

 A relatively straightforward story of another copied protocol who were too ambitious with their imitation. 

 The era of BSC flash loans is upon us, and this won’t be the last time we see such attacks.

 $30 million reward for only $66 in fees is an excellent ROI, and with so many developers rushing to copy the ETH blue chips onto BSC, there’s sure to be more opportunities for keen eyed hackers.

 With no word yet from CZ or Binance, one wonders, how much of this will they tolerate?

 How rekt do you have to get for CZ to step in and save you? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

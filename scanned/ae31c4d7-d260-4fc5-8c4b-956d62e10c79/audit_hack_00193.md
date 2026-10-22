# [C] PancakeBunny exploit: “Aren’t Flash loans Earitating” said the hacker

## Summary
Severity: Critical
Target: PancakeBunny
Loss: $45,000,000
Published: 05/19/2021
Source: https://rekt.news/pancakebunny-rekt
Type: rekt-postmortem

## Details
## PancakeBunny - REKT

 Thursday, May 20, 2021 PancakeBunny - BSC - REKT 

 read this article also in : zh 

 “Aren’t Flash loans Earitating” said the hacker . 

 $45 million gone from Pancake Bunny Finance. 

 This was made possible due to a bug in the protocol that uses PancakeSwap to retrieve the prices of PancakeSwap liquidity providers (BNB-BUSDT / BNB-BUNNY)

 8 flash loans were used to manipulate the price on various PancakeSwap pools, creating a skewed calculation of BUNNY from the VaultFliptoFlip vault.

 This led to the minting of 697,000 BUNNY tokens, which were then sold, causing the price to drop from $146 to $6.

Credit: Peckshield 
 BSCScan Transaction. 

 Step 1: Take 8 different flashloans:

 The first seven flashloans are taken from various PancakeSwap pools while the last comes from Fortube Bank. 

 1.05M WBNB from WBNB+CAKE pool

 522.52K WBNB from WBNB+BUSD pool

 210.16K WBNB from WBNB+ETH pool

 133.50K WBNB from WBNB+BTCB pool

 241.02K WBNB from WBNB+SAFEMOON pool

 98.519K WBNB from WBNB+BELT pool

 66.29K WBNB from WBNB+DOT pool

 2.96M USDT from Fortube Bank.

 Step 2: Deposit 2.96M USDT and 7886 WBNB into WBNB+BUSDT pool as liquidity and mint 144.45K LP tokens.

 Step 3: Swap 2.32M WBNB for 3.83M BUSDT via the above WBNB+BUSDT pool so that the pool has a sufficiently large WBNB reserve, which is used to influence the valuation of the pool tokens.

 Step 4: Call getReward() to claim rewards from VaultFlipToFlip. With the higher LP token valuation, the attacker is able to claim a reward of 6.97M BUNNY (valued about $1+ B). Note the dev team gets separate 1.05M BUNNY.

 Step 5: Return the flashloans in Step 1 back to PancakeSwap pools and Fortube Bank.

 The attacker’s loot was initially held in this wallet: 0xa0acc61547f6bd066f7c9663c17a312b6ad7e187.

 At its peak, Pancake Bunny had over $10 billion in TVL. 

 At the time of writing, that TVL is down to just over $1 billion. 

 Even a Haechi audit couldn’t protect the Pancake Bunny from the awesome power of flash loan attack, earning them joint third position on the rekt leaderboard. 

 Yesterday was a brutal day for all crypto markets, but BSC users in particular must have felt under fire, as Venus Protocol and “wArOnrUgS” imploded within hours of each other.

 Loyal readers will have noticed that our anonymous author was unfortunately unavailable on such an eventful day. 

 We are always recruiting community members for our research and OPSEC departments.

 Will you help us in our quest to document corruption and exploitation in crypto and DeFi? 

 If you have any suggestions or contributions towards our leaderboard or our content in general, please add to the rekt repo , or contact us on Twitter , Telegram , or via email using the address below.

 EDIT - 18th July 2021. 

 Haechi reached out to us with the following statement:

 We audited their smart contracts and published a report. This warned the fact that there are non-audited and changeable external contracts and the “helper” function is weak to flash loans’ attack. Pancake Bunny team upgraded their smart contracts and chose another auditing team for the updated contracts. This flash loan was caused by new smart contracts we did not audit.

 You can find the details here. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

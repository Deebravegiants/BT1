# [C] Popsicle Finance exploit: A complex hack of a simple bug leaves Popsicle Finance in a sticky situation

## Summary
Severity: Critical
Target: Popsicle Finance
Loss: $20,000,000
Published: 08/03/2021
Source: https://rekt.news/popsicle-rekt
Type: rekt-postmortem

## Details
## Popsicle Finance - REKT

 Wednesday, August 4, 2021 Popsicle - REKT 

 read this article also in : zh 

 Meltdown. 
 ~$20 million gone.

 A complex hack of a simple bug leaves Popsicle Finance in a sticky situation.

 The RewardDistribution bug has already been exploited in several other protocols. 

 Auditors and Smart contract developers need to stay up to date. This code should not have made it to production. 

 If only there was somewhere they could read about previous hacks and exploits... 

 Credit: @Peckshield & @Mudit__Gupta 

 Attacker address: 0xf9E3D08196F76f5078882d98941b71C0884BEa52 

 Transaction Hash: 0xcd7dae143… 

 The “Sorbetto Fragola” contract automatically manages Liquidity on Uniswap V3. Fragola adjusts the position so it is always in the correct range.

 The hack was due to the lack of proper fee accounting when LP tokens are transferred. 

 Specifically, the attacker creates three contracts: A, B, and C and repeats in the sequences of: 

 A.deposit(),

 A.transfer(B),

 B.collectFees(),

 B.transfer(C),

 C.collectFees() for eight pools.

 Step 1: Flashloan 30M USDT, 13K WETH, 1.4KBTC, 30M USDC, 3M DAI and 200K UNI from Aave to attack eight PLP pools.

 Below we take the USDT-WETH pool as an example. 

 Step 2: Alice calls deposit() to add 30M USDT and 5.467K WETH liquidity into the USDT-WETH PLP pool and gets 10.51 PLP tokens.

 Step 3: A transfers the 10.52 PLP tokens to B

 Step 4: B calls the collectFees() function to get its tokenRewards updated.

 Step 5: B transfers the 10.52 PLP tokens to C

 Step 6: C calls the collectFees() function to get its tokenRewards updated.

 Step 7: C transfers the 10.52 PLP tokens back to A, so A will be able to remove the liquidity later on.

 Step 8: A calls withdraw() to remove the liquidity and gets back 30M USDT and 5.46 WETH.

 Step 9: B calls collectFees() to get 2.15M USDT and 392 WETH as rewards.

 Step 10: C calls collectFees() to get 2.15M USDT and 402 WETH as rewards.

 Step 11: The attacker repeats step 2 to 10 for several other PLP pools and repays the flashloan in step 1.

 A portion of the attack's profits (4,100 ETH, about $10M) is immediately deposited to Tornado Cash. 

 At the time of writing, the remaining 2,560 WETH, 96 WBTC and 159,928 DAI are still in the attacker account: 0xf9E3D08196F76f5078882d98941b71C0884BEa52. 

 Everyone makes mistakes, but not many are responsible for $20M TVL… 

 It’s strange that Peckshield decided to publish a post-mortem of code that they audited, instead of waiting and releasing it as an official release from the Popsicle account.

 Another client's funds lost, while Peckshield chase clout on Twitter. 

 There is little excuse for the auditors for missing an already known bug.

 They did write a nice post-mortem though, so at least Popsicle Finance got something for their money. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

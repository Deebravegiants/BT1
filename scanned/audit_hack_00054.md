# [H] BurgerSwap exploit: The hackers are really spoiling us this week with our fourth helping of the exact same meal

## Summary
Severity: High
Target: BurgerSwap
Loss: $7,200,000
Published: 05/28/2021
Source: https://rekt.news/burgerswap-rekt
Type: rekt-postmortem

## Details
## BurgerSwap - REKT

 Friday, May 28, 2021 BurgerSwap - REKT 

 read this article also in : zh 

 The hackers are really spoiling us this week with our fourth helping of the exact same meal.

 Can you ever really get tired of a classic? 

 BurgerSwap was the next in a growing line of protocols to fall victim to the same hack that has been causing issues in recent weeks.

 Since the market crash, this type of Drive-thru convenience exploit has been flavour of the month, and yet protocols still seem completely oblivious to this weakness in the contract. It’s as if they welcome these hacks with open arms, turning their backs to the counter and feigning surprise as people leave without paying.

 It certainly appears as though even the easiest jobs can be royally messed up. BurgerSwap simply had to copy UniSwap’s code and yet there was something missing from their order.

 The question has to be asked, was this negligence? Or something a little seedier? 

 Back to flipping burgers...

 At around 3 am on May 28th (UTC+8), $7.2M was stolen from #BurgerSwap in just 14 servings.

 Thieves managed to make off with the following:

- 4.4k WBNB ($1.6M)

- 22k BUSD ($22k)

- 2.5 ETH ($6.8k)

- 1.4M USDT ($1.4M)

- 432k BURGER ($3.2M)

- 142k xBURGER ($1M)

- 95k ROCKS

 And each attack looked like this:

- 
 Flash swap 6k WBNB ($2M) from PancakeSwap.

- 
 Swap almost all WBNB to 92k BURGER on BurgerSwap.

- 
 Hackers created their own fake coin (a non-standard BEP-20 token) and formed a new trading pair with $BURGER of 100 fake tokens and 45k BURGER.

- 
 The 100 fake tokens were then swapped to 4.4k WBNB through the pool from step 3.

- 
 Attacker then made another swap from 45k BURGER to 4.4k WBNB.

- 
 In total the attacker received 8.8k WBNB for the two latest steps.

- 
 Swap 493 WBNB to 108.7k BURGER on BurgerSwap.

- 
 Repay flash swap.

Credit: @FrankResearcher 
 This exploit was made possible by the fact that the attacker could do reentrance and make a second swap before reserves, which are used to calculate the number of tokens in swaps, were updated.

 Interestingly though, this seems to have been enabled by by a missing x*y=k check. Something which was present in the original univ2pair contract but was seemingly removed in this instance.

 It seems unlikely that the developers at BurgerSwap would be so careless in their coding but what is the alternative? With the x*y>k check removed, anyone can trigger a swap of any output size while paying only one unit of the input token, a deal straight from the saver menu.

 The number of hacks we have seen of projects on the BSC over the past week has been off the charts. This whole situation is eerily reminiscent of what happened in Autumn last year on ETH. A disappointing special offer which no-one wanted to see make a return.

 While no-one likes to see the customers get short changed, it is increasingly difficult to find sympathy for rogue, copycat entrepreneurs who try to emulate and profit from a tried and tested recipe, but who don’t care enough about the consumer to check the ingredients of their products, risking the health of the very people they derive profit from.

 That said, if you eat at a McDaniels or Burger Duke, are you not at least partly responsible for your own indigestion? 

 BurgerSwap claims they are in the process of producing a detailed compensation plan for their customers. A welcome relief for many whose stomachs have been turned by this whole affair.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

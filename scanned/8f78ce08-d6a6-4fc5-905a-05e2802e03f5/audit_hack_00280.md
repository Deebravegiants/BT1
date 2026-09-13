# [C] Uranium Finance exploit: Uranium Finance has exploded, and not for the first time

## Summary
Severity: Critical
Target: Uranium Finance
Loss: $57,200,000
Published: 04/28/2021
Source: https://rekt.news/uranium-rekt
Type: rekt-postmortem

## Details
## Uranium Finance - REKT

 Wednesday, April 28, 2021 Uranium - REKT 

 read this article also in : zh 

 Uranium Finance has exploded, and not for the first time. 

 The BSC Uniswap clone played around too much with their copied code and left a loophole open for someone to take the funds.

 At least $57,000,000 was taken due to a simple math bug introduced to the UraniumPair contracts which had been forked from the Uniswap v2 code.

 Uranium Finance had already suffered a prior exploit of their rewards contract earlier this month, when they introduced vulnerabilities into the MasterChef contract.

 At least 2,200 ETH from the latest incident have already been mixed through Tornado.cash, from a total amount worth approximately $57.2 million at the time of writing.

 Co-founder of bzX Kyle Kistner pointed out the small change in the UraniumPair contract that had such dramatic effects:

 VS 

 Did you spot the difference? 

 1,000 was changed to 10,000 in two places but not at the end.

 This resulted in being able to swap 1 wei of the input token for 98% of the total balance of the output token.

 This ultimately breaks the check for the Uniswap v2 x * y = k “constant product” formula before updating fee-adjusted reserve balances. Credit: 0xdeadf4ce 

 The following funds were removed: 

- 34k WBNB ($18M)

- 17.9M BUSD ($17.9M)

- 1.8k ETH ($4.7M)

- 80 BTC ($4.3M)

- 26.5k DOT ($0.8M)

- 638k ADA ($0.8M)

- 5.7M USDT ($5.7M)

- 112k U92

 Before interacting with Uranium, the attacker sent the minimum amount of each token to pair contracts. 

 After that, they used a low-level function swap() whose execution should drain both reserves.

 The Uranium team migrated the contract to v2 about ten days ago, and the old version did not have this bug.

 The team then decided to update the protocol to v2.1, in which the only significant change is the fix of the above-mentioned bug. The liquidity migration from v2 to v2.1 was supposed to start today.

 So they added a bug in v2, left it for ten days, and on the day they were due to fix it, it was exploited. 

 To make things even more suspicious, we note that the Uranium contracts repository has been removed from Github.

 Credit : igor igamberdiev 

 Did the Uranium team add in the bug and use the liquidity migration to try and hide it? 

 Or did “somebody” “find out” about the bug and exploit it just before the developers managed to fix it? 

 Cross chain hacks are becoming more common. 

 The BSC system is not as closed as it once was. There are multiple bridges out of BSC now, and they’re not all controlled by Binance, meaning CZ can’t blacklist all the addresses and keep the stolen funds on BSC.

 Attackers will steal on one chain and escape to another where they can’t be tracked so easily. Tornado is currently the only DAPP allowing for this kind of exit, but we’ll soon see clones on other chains.

 The beneficiary of this incident is now sat on $57.2 million of liquid assets, a much more preferable prize than the EASY tokens of our previous article, and one which places them in second place on our leaderboard .

 Exploits and rug pulls will slow down, but they’re unlikely to stop completely. Even now, when we have battle tested code such as Curve and Uniswap, users still look to chase higher returns in untested projects, so for now, rug pulls look set to stay.

 One day hackers will operate on fully private chains where they have no need to escape with their funds, but until then...

 rekt will be watching. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

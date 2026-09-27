# [C] Rari Capital exploit: After a quick break for lunch, it was Rari Capitals turn to get rekt

## Summary
Severity: Critical
Target: Rari Capital
Loss: $10,000,000
Published: 05/08/2021
Source: https://rekt.news/rari-capital-rekt
Type: rekt-postmortem

## Details
## Rari Capital - REKT

 Saturday, May 8, 2021 Rari Capital - REKT 

 read this article also in : zh 

 Young blood and new money. 

 After a quick break for lunch, it was Rari Capitals turn to get rekt.

 The youthful yield aggregator has fallen victim to a serial attacker, as the same wallet which attacked Value DeFi only hours before, turned their eyes onto the Rari Capital ETH pool , removing $10 million worth of ETH.

 Rari Capital has attracted attention due to the young age of their developers, causing the community to argue amongst themselves as to whether age is of much relevance when the whole DeFi industry is only 2 - 3 years old.

 Although some might say they “ had it coming ”, we take no pleasure in learning that people have lost their money. 

 There are no developers with 10 years experience in DeFi system design, this is a meritocracy that depends on the skill and maturity of the person rather than the length of their CV.

 Each attack presents us with a valuable lesson, and we must study the techniques in order to build a safer future. 

 We’re looking at the actions of a cross-chain killer, who used the blood money from Value DeFi to fuel their attack on Rari Capital. 

 5,346 BNB ($3.8M) were stolen and swapped to 1k ETH.

 The attacker’s actions on BSC were as follows: 

 1: Create a fake token and pool it with BNB on PancakeSwap in order to use Alpaca Finance.

 2: Interact with Alpaca Finance, where when calling approve() for a fake token, a payload is called, which allows an attacker to use VSafe through Codex farm to get vSafeWBNB

 3: Convert vSafeWBNB to WBNB

 4: Transfer WBNB to Ethereum through Anyswap.

 Repeat 2x. 

 The attack on Rari was as follows: 

 1: Create a fake token and pool with it on SushiSwap

 2: Interact with Alpha Homora , where a payload is also called so that the attacker can get ibETH in the Rari ETH pool contract.

 3: Convert ibETH to ETH in the Rari ETH pool.

 As a result, 2.9k ETH ($11.1M) was stolen, and another 1.7k ETH was at risk before the actions of the Rari team.

 The total profit from the two attacks was $15M in ETH. 

 credit: frankresearcher 

 The Rari Capital governance token $RGT fell sharply in price following the attack.

 The attacker decided to voice their opinion on the involved protocols, but it seems they had second thoughts, as they tried to cancel the transaction. However, they set the gas too low and the cancellation didn’t go through for 20 minutes, giving everyone time to see their message.

 Credit: banteg & dudesahn 

 This attack technique was similar to the Evil Pickle Jar , one which looks likely to become even more common in the future. 

 Even though various protocols were used, the same exploit mechanism was applied.

 Alpaca/Alpha, vSafe/Rari, PancakeSwap/SushiSwap - the interaction between them was built in such a way that the exploit was easily repeated on another chain.

 The interoperability between DeFi protocols is increasing, and the blurred lines make for even easier escape routes.

 In the roaring twenties, the ruthless are rewarded, and any prosecution seems unlikely. 

 With so many other surface-level crimes in crypto, who’s going to try and prosecute someone for exploiting contracts where so many remain anonymous? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

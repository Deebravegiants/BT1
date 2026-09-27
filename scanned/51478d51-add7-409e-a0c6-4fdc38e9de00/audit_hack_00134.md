# [C] Inverse Finance exploit: A professionally executed hack allowed an anonymous actor to manipulate the price of INV and help themself to an exclusive deal from the ETH based len

## Summary
Severity: Critical
Target: Inverse Finance
Loss: $15,600,000
Published: 04/02/2022
Source: https://rekt.news/inverse-finance-rekt
Type: rekt-postmortem

## Details
## Inverse Finance - REKT

 Saturday, April 2, 2022 Inverse Finance - REKT 

 read this article also in : zh 

 Inverse Finance got flipped for ~$15M. 

 This attack got the experts attention. 

 A professionally executed hack allowed an anonymous actor to manipulate the price of INV and help themself to an exclusive deal from the ETH based lending protocol.

 How did it happen?

 Credit: Igor Igamberdiev & Peckshield. 

 ~$15.6M was stolen in the form of: 

- 1588 ETH

- 94 WBTC

- 4M DOLA

- 39.3 YFI

 First of all, the exploiter withdrew 901 ETH from Tornado Cash. 

 Then they transferred 1.5 ETH to 241 clean addresses via Disperse and deployed five different smart contracts, of which only one was real.

 He then swapped 500 ETH to 1.7k INV so that it went through the INV-WETH pair on SushiSwap, significantly changing the price due to low liquidity (50x).

 At the same time, he began spamming transactions with an exploit to be the first to get into the next block and get an inflated price from SushiSwap.

 The Inverse Finance oracle, through Keeper Network, ended up using SushiSwap TWAP as an oracle, returning the price that made the INV token on the platform incredibly expensive.

 The attacker then deposited his 1.7k INV (fair price - $644k) as collateral and (permanently) borrowed $15.6M.

 Peckshield provided the following visualisation. 

 We would prefer that hackers take the weekends off, but at least this wasn’t another case of “compromised keys”. 

 Inverse Finance have since released their official statement , and several knowledgeable community members have pointed out the complexity / efficiency of the attack technique.

 Flash bot expert himself, @bertcmiller , said that:

 "The InverseFinance hack is one of the most MEV aware hacks I've seen."

 "[the attacker] held an oracle's price at an insane level across multiple blocks, prevented arb bots from bringing prices back in line, and protected against generalised frontrunners."

 Chainlinkgod , (who always has something to say when an oracle is exploited) also pointed out that:

 "Relying upon a TWAP oracle generated from a single thinly traded DEX trading pair with a short time sample compounds market manipulation risks."

 After the attack, in Twitter Spaces, Inverse Finance stated that they are working with Chainlink to launch a INV price feed once liquidity requirements have been met. This would then replace the current TWAP oracle.

 Although these risks are obvious in hindsight, it’s clear that this was not an amateur job. 

 Even the best in the business wear black hats sometimes… 

 Maybe it’s better not to aggravate them.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

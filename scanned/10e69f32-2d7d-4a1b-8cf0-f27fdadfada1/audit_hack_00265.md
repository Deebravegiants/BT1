# [H] The Big Combo (Growth DeFi - REKT) exploit: Millions of dollars gone but nobody blinks an eye

## Summary
Severity: High
Target: The Big Combo (Growth DeFi - REKT)
Loss: $1,300,000
Published: 02/09/2021
Source: https://rekt.news/the-big-combo
Type: rekt-postmortem

## Details
## The Big Combo (Growth DeFi - REKT)

 Tuesday, February 9, 2021 BT Finance - Growth DeFi 

 read this article also in : zh 

 The days blur into one.

 Locked down, wired up and worn out. 

 Millions of dollars gone but nobody blinks an eye.

 Seems to be the first time we hear about some of these protocols is when they get arbed into the limelight by hackers using the same old attack vectors. 

 BT Finance? Growth DeFi? Small name backstreet protocols are easy prey for the serial killers who roam these streets without fear.

 We’ve been through this before, you know the deal. Manipulate the price, call earn, and withdraw the loot. Nothing new under the sun, why change the plan if it always works? 

 BT Finance would have been stopped by a copyright claim if the hackers hadn’t got to them first, so they were already set to fail. For the few users who were tempted in by their sultry slogan of “Best yield for tokens”, maybe they should have seen this coming…

 If you’re depositing your money into a protocol that is trying something new, or competing with what’s currently on offer, then taking on a certain level of risk can be justified. However, these low quality copycat bits of code are by and for simple gamblers who don’t look long term.

 So BT Finance done , no surprise. 

 $1.5 million . Flash in flash out, like taking candy from a baby. Is a Peckshield audit supposed to be deterrence or encouragement for a hacker? At this point it’s not quite clear.

 Growth DeFi had a little more to them. 

 Although their product was nothing new, they worked hard and built up a user base before eventually falling victim to a slightly more exotic attack than the usual.

 By forcing the staker contract to accept a liquidity pair containing a fake token, the attacker was able to remove $1.3 million in liquidity.

 The attacker created a fake token called AXZ and supplied rAXZZ/GRO liquidity. He then staked it in the contract and pulled out the other pair.

 @r0bster97 summarised the attack.

 First transaction :

 Swap 0.001 $ETH for ~0.0148 $GRO 

 Second transaction :

 ~0.0148 $GRO and 100,000,000,000 $AXXZ liquidity to Uniswap

 Third transaction :

 Remove ~27,516 $GRO and ~1,218 $rAAVE liquidity from Uniswap.

 "Missing if-condition in the smart contract code"

 Fourth transaction :

 Swap ~27,516 $GRO for ~597 $ETH on Uniswap.

 Payday. 

 The Growth DeFi team has provided a further analysis of the attack on their Medium page here .

 Two attacks, two techniques, the same end result. 

 $2,7 million combined, taken with little to no consequence.

 Just another day in the wild west phase of DeFi.

 Money always moves to the smartest players, whether that’s through deception or not is irrelevant. 

 Don’t rely on audits to do your diligence for you, check the code yourself or work with people that can.

 In a game where the smartest players are trying to outsmart each other, all the small guys can do is try to play safe. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

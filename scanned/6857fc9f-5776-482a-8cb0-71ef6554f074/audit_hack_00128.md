# [H] Hundred Finance exploit: Hundred Finance finally gets its very own article

## Summary
Severity: High
Target: Hundred Finance
Loss: $7,400,000
Published: 04/15/2023
Source: https://rekt.news/hundred-rekt2
Type: rekt-postmortem

## Details
## Hundred Finance - REKT 2

 Tuesday, April 18, 2023 Hundred Finance - REKT 

 read this article also in : zh 

 Hundred Finance finally gets its very own article. 

 No sharing the spotlight this time… 

 Shortly after 2pm UTC on April 15th, Hundred Finance suffered a $7.4M exploit on Optimism.

 The team’s announcement sounded more like a bystander’s observation than a protocol informing users of a multimillion dollar hack…

 It looks that Hundred got hacked on #Optimism. We will update when there is more information to it.

 But, then again, Hundred have been through all this before. 

 Last February, Hundred caught a stray to the tune of 3.3M when Meter got rekt .

 The following month saw Hundred’s leaderboard debut , when $6.2M was lost on xDAI chain to a dual-edged attack which also hit Agave DAO for $5.5M.

 That time, the attack vector was the same reentrancy mechanism which hit CREAM Finance in August 2021.

 With Hundred’s leaderboard total now standing at $16.9M… 

 …what was it this time? 

 Credit: Daniel Von Fange , Peckshield , Beosin , Numen Cyber 

 Hundred is a Compound fork which uses hTokens to track lending positions. It was audited in Feb 2022 by WhiteHatDAO.

 As Daniel Von Fange points out :

 the project setup two wBTC cTokens, one of which was used by the UI, one of which was empty.

 Using a flashloan of WBTC from Aave, the attacker was able to donate large amounts of WBTC to the empty hWBTC contract, manipulating the exchange rate between hWBTC and WBTC. To top it off, the redeemUnderlying function contained a rounding error.

 Attacker’s address ( OP , ETH ): 0x155da45d374a286d383839b1ef27567a15e67528 

 Hack tx 1: 0x6e9ebcde… 

 Hack tx 2: 0x15096dc6… 

 Peckshield summed up the exploit as: 

 The root cause appears the attacker donates 200 WBTC to inflate hWBTC's exchange rate so that even a tiny amount (2 wei) of hWBTC can basically drain current lending pools.

 Beosin also provided a step-by-step analysis: 

 The root cause is that the attacker can manipulate the exchangeRate by donating a large amount of WBTC to the hWBTC contract.

 In the getAccountSnapshot function, the value of exchangeRateMantissa relies on the amount of WBTC in the contract.

 The attacker flashloaned 500 $WBTC, then called the redeem function to redeem the previously staked 0.3 WBTC.

 Next, the attack contract 1 sent 500.3 WBTC to attack contract 2. Contract 2 used 4 BTC to mint 200 hWBTC. The redeem function was then called to redeem the 4 BTC.

 Here the attacker can redeem the 4 WBTC previously staked with less than 200 hWBTC. At this point the attacker had a very small amount of hWBTC left on contract 2.

 Attack contract 2 then sent 500.3 WBTC to the hWBTC contract and borrowed 1021.91 ETH via the remaining 2 hWBTCs.

 Finally the attack contract 2 repaid the previous debt by using 1 hWBTC, and withdrew 500.3 WBTC from the contract.

 The attacker bridged most of the stolen funds to ETH where centralised stables USDT and USDC were swapped, or deposited into Curve.

 At the time of writing, the hacker’s debank profile shows approximately $5.4M of assets on Ethereum and $0.9M remaining on Optimism. 

 The price of HND token dropped around 50% over the day following the hack. It has since recovered somewhat, to ~$0.025, down from ~$0.039 before the attack.

 As we wrote last time : 

 Forks upon forks create a house of cards. If the code is copied and pasted, vulnerabilities can open up where they're least expected.

 When one fork falls, all others have to check their foundations.

 Hundred have advised other COMP forks to get in touch, warning that the hack exploited “ a general flaw in the code and not specific to Hundred deployment ”. 

 Likely spurred on by Euler Finance ’s recent success, the Hundred team have announced a reward for info leading to identification of the hacker:

 48h passed since we sent an on-chain message to the hacker and tried to start negotiations with him.

 Today we are launching a $500k reward in the hope that this provides additional incentive for info that leads to the Hundred attacker’s arrest and the return of all funds.

 Hopefully the added pressure is as effective in recovering the funds…

 Will Hundred get lucky? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

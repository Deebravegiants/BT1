# [C] Harvest Finance exploit: A skilled farmer used flash loans to reap $33.8 million from the FARM_USDT and FARM_USDC pools

## Summary
Severity: Critical
Target: Harvest Finance
Loss: $25,000,000
Published: 10/26/2020
Source: https://rekt.news/harvest-finance-rekt
Type: rekt-postmortem

## Details
## Harvest Finance - REKT

 Monday, October 26, 2020 harvest finance - flash loan - hack 

 read this article also in : zh 

 The reaper does not listen to the harvest. 
 A skilled farmer used flash loans to reap $33.8 million from the FARM_USDT and FARM_USDC pools.

 In troubled times, some turn to sacred texts for guidance.

 Of the ten plagues that ruined the harvests of ancient Egypt, the first brought blood, and the second; frogs.

 It was Baron Rothschild who advised to buy when there’s blood in the streets.

 Now that the heady days of DeFi summer are over, the DFI-PERP has taken on a sanguine liquidity, and the behaviour of the more Enlightened Farmers has become decidedly unchristlike.

 In Exodus 7:25 8-15, we read

 “I will plague your whole country with frogs. The frogs will go up on you and your people and all your officials.” 

 In our cryptographic metaverse, the developer is the official, and as was prophesied in the ancient scrolls, the Harvest Finance developers have certainly got frogs all up on them.
 
 Arbitrage Analysis 

 fUSDT fell 13.7% and $FARM fell 67% over two hours as the hacker took out a $50m USDT flash loan, then used the Curve Finance Y pool to swap funds and stretch stable coin prices out of proportion.

 Detailed transaction analysis here. 

 The following actions took place in a 7 minute time period. Credit @valentinmihov 

- 
 Swap 11.4m USDC to USDT -> USDT price up

- 
 Deposit 60.6m USDT into Vault

- 
 Exchange 11.4m USDT to USDC -> USDT price down

- 
 Withdraw 61.1m USDT from Vault -> 0.5m profit

- 
 Rinse and repeat 32 times. (without any prior testing)

- 
 Convert to renBTC and exit to BTC / ETH via Tornado Cash

 The attacker was able to withdraw more USDT at step 4 because of the changed USDT price. As the price of USDT was lower during the time of the withdrawal, their shares represent more USDT from the Vault pool.

 Approximately 4 cycles can fit into a 10m gas limit, and although the profit on each cycle is less than 1%, ~$500k per repetition adds up quickly.

 The price calculation mechanism for LP deposits and withdrawals was the source of the exploit, meaning this attack could have carried over to the renBTC pool, the FARM_TUSD pool, and the FARM_DAI pool. However the hacker chose to stop after draining $25m or 17% of what was available in the FARM_USDT and FARM_USDC pools, although they could have easily continued to drain the entire pool for a total of $400m if they had so desired.

 The FARM_USDT strategy has the following code
 
Which indicates some price index was calculated. 
 However, since they specify "tokenIndex", we can assume they aren't just using get_virtual_price() but instead, do some underlying calculation.
Credit Andre Cronje 
 
The arbitrage check function tolerance value was not high enough, but the default slippage tolerance value of 3% was too high. 
 Credit PancakeBunnyFin 

 It wasn’t just the hacker who profited from their actions. LPs and Harvest developers also received a reasonably sized sum of money, as the hacker chose to throw back some scraps ($2,478,549.94) to the Harvest Deployer in the form of USDT and USDC.

 Harvest have since stated that this will be returned to the affected users pro-rata using a snapshot.

 No hacker.Just a simple* $24M (0x53f) juicy arb on @harvest_finance 

 $50M USDC flash loan @UniswapProtocol 
Swap $11M (USDC/USDT) @CurveFinance 
~61M on fUSDT Vault
Swap $11M USDT/USDC yUSDT
Withdraw $61M with $0.5M profit
Repeat & clean into @TornadoCash t.co/nFTuyU3s6w pic.twitter.com/2oXQ2PsY32 > — Julien Bouteloup (@bneiluj) October 26, 2020 

 Lucky Liquidity Providers Profit 

 The approximate figures are as follows. Credit Jiecut42 

 Hacker - $24,000,000

 Uniswap LPs - $6,000,000

 Harvest Developers - $2,500,000

 Curve LPs - $1,000,000

 Ethereum Gas - $100,000

 RenVM fees $20,000

Credit BitcoinWhiskers for the sweet pie. 
 With exposure to all Curve pools, veCRV holders have profited from the extra volume going through Curve, as the hacker generated ~$500k in trading fees which will be shared among all those who are staking their CRV.
Curve trading fees increased over 8,000% from the previous day as the hacker swapped over $100M in USDT and USDC.
 
Uniswap LPs also had a field day thanks to the actions of this anonymous superfarmer. 
 Total Uniswap trade volume spiked from $148 million to $1 billion in 24 hours.

 92% of this volume came from the USDT/ETH and USDC/ETH pairs, generating $5.76 million in fees for liquidity providers.

Credit Larry Cermak 
 Confidential Contributor 

 Whistleblowing and protecting our contributors is a huge part of what we do at Rekt. While your author was writing this story, someone contacted us with information regarding the actions of Harvest Finance some days prior to last nights events.

 The following information is presented without comment.

 I was contacted by the Harvest Finance team seeking collaboration on incentivising liquidity pools for two asset classes. 

 The first was trustless BTC, the second was FARM/ETH. 

 I didn’t follow up with them as something was off-putting. 

 I’m not claiming that it is the Harvest team, but seeing the 3% slippage in the smart contract, and the fact that the exploit was in trustless BTC, which is a “novelty”... 

 I think that if this isn’t Julien, then it has to be Harvest Finance themselves, or the EMN hacker, or someone with deep flashloan knowledge. 

 Refund Requests 

 As usual, a debate has arisen regarding the ability for protocols to block or amend this type of activity in the future. In the Curve Telegram group, some were of the opinion that Curve should be able to block this type of activity, however the existing smart contracts cannot be stopped or modified.

 There have also been calls for renBTC to refund the fees they earned from the hackers activity. This is a controversial topic which forces users to consider the pros and cons of using decentralised protocols.

 Sloppy Security 

 Only three weeks ago on October 6th, Harvest Finance published a security update stating that they were ensuring the safety of their lands via “rigorous security audits” from Peckshield , Haechi Labs , and CertiK .

 It should be noted that Peck Shield and CertiK also audited Bzx before their three hacks earlier this year.

 We await their comments on this situation.

 Developers and seemingly even specialised security firms are not used to having to consider the impact of flash loans on their code.

 Mastering flash loans is like turning up to a 12th century jousting tournament on a Harley Davidson dual-wielding AK47’s; nobody expects it, plebs get rekt, and it’s years until the uneducated masses are able to protect themselves from such savage master tradesmen.

 Harvest Finance has responded to the events with an enjoyably passive-aggressive tone.
 
 twitter.com/harvest_finance/status/1320624369543057409 

 Truthful Terminology 
 Arbitrage / Exploit / Hack.

 The differences in the terminology become increasingly blurred, while the fact that “code is law” becomes crystal clear.

 The term used by Harvest Finance was arbitrage economic attack. Some consider this activity a crime, while others simply see the actions of a more capable user, yield farming with modern machinery.

 Is this a meritocracy, or anarcho-capitalism?

 It’s certainly entertaining either way.

 caveat emptor. 

 It is only the farmer who faithfully plants seeds in the spring, who reaps a Harvest in the autumn. B.C. Forbes 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

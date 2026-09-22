# [C] BonqDAO exploit: But the anonymous attacker got away with less than $2M

## Summary
Severity: Critical
Target: BonqDAO
Loss: $120,000,000
Published: 02/01/2023
Source: https://rekt.news/bonq-rekt
Type: rekt-postmortem

## Details
## BonqDAO - REKT

 Friday, February 3, 2023 BonqDAO - AllianceBlock - REKT 

 read this article also in : zh 

 BonqDAO got bonked for $120M. 

 But the anonymous attacker got away with less than $2M. 

 The Polygon-based lending and stablecoin protocol was hit by a two-stage attack on Wednesday in another example oracle manipulation.

 The alarm was raised on Twitter by @spreekaway , who live-tweeted the dumping of stolen funds. The affected protocols, BonqDAO and AllianceBlock (whose ALBT token was used in the exploit), both confirmed the hack in the following hours.

 Despite all the action being visible on-chain, BonqDAO telegram admins attempted to downplay the incident whilst the team presumably worked out what had happened.

 FUD and spam will not be tolerated

 rekt.news reckons: “using instant price feeds for collateral valuation will not be tolerated.” 

 Credit: Peckshield , Beosin 

 Attacker’s address: 0xcacf2d28b2a5309e099f0c6e8c60ec3ddf656642 

 Example attack tx: 0x31957ecc… 

 Attacked smart contract: 0x8f55d884cad66b79e1a131f6bcb0e66f4fd84d5b 

 Samczsun summarised the attack as follows:

 the attacker said "btw 1 ALBT = 5 billion MATIC now" and Bonq said "ok"

 The hacker was able to manually update the Tellor price feed of (wrapped) WALBT collateral by staking 10 TRB tokens (worth just ~$175).

 The attacker then used the submitValue function to report WALBT price to the oracle and, because BonqDAO uses the instant value, the attaker was able to borrow against their inflated collateral within the same tx. 

 Firstly, the ALBT price was raised, allowing the attacker to mint 100M BEUR, Bonq’s Euro-pegged stablecoin against 0.1 WALBT collateral.

 Then, in a subsequent transaction, the WALBT price was reset to extremely low, allowing the attacker to liquidate user’s WALBT collateral, and netting approximately 113M WALBT.

 Beosin provided a step-by-step: 

 The attacker calls the depositStake function of the TellorFlex contract, depositing 10 $TRB. Why 10 TRBs? We can see that the takeAmount is exactly 10*10^18

 Next, the hacker calls the submitValue function to submit a request to change the $WALBT price. The function determines if the caller's stake amount has reached the pre-set takeAmount, which is why the attacker needs to first stake 10 TRB tokens (10^18 is decimal point).

 This function will record the price submitted by the caller, in this case 50000000000000000000000000000000.

 After the price is set, the hacker calls the createTrove function of the Bonq contract to create the trove(0x4248FD) contract, which is a contract of data recording, borrowing and liquidating. Next, the attacker stakes 0.1 $WALBT to the contract to perform a borrowing operation.

 Normally, the borrowing amount should be < 0.1 WALBT to ensure collateral rate in a safe range. But in this contract, the calculation of the collateral value is via TellorFlex contract. The attacker has already raised $WALBT price, thus being able to borrow 100M $BEUR.

 The hacker sets $WALBT to a low price in 2nd TX. When the $WALBT price is extremely low, the stake rate of WALBTs staked by other users will be at liquidation, enabling hacker to liquidate $WALBT staked by other users at low cost, eventually obtaining ~114M WALBT.

 —

 Losses have been widely reported to be up to $120M, using the tokens’ prices at the time of the hack. But low liquidity meant the attacker has only managed to swap the loot to around $1.7M worth of ETH and DAI, so far. 

 Nevertheless, the damage to BonqDAO was brutal, with TVL drained from ~$13M yesterday to just over $100k at the time of writing. 

 Stolen BEUR was dumped on Polygon for just over $500K. Funds were then sent to the attacker’s Ethereum address , where the ALBT was repeatedly dumped for ETH. The attacker’s ETH address currently holds 711 ETH (~$1.2M) and 535k DAI, as well as 89M ALBT (supposedly worth ~$3M, if the attacker can find somewhere to sell it…).

 BlockSec provided a detailed flowchart of funds, which can be found here . The attacker’s ETH address was funded via Tornado Cash shortly before the attack, and the stolen funds have since been deposited back into the mixer.

 Omniscia’s audit of BonqDAO raised concerns over “ multiple vulnerabilities as well as core design flaws ”.

 According to Omniscia's post-mortem , BonqDAO decided to:

 not move forward with the implementations audited at the time, opting to integrate Chainlink oracles in the future.

 The Bonq Protocol has introduced numerous updates since the time the audit was finalized, including all contracts involved in the vulnerability (ConvertedPriceFeed, ChainlinkPriceFeed, and TellorPriceFeed). These contracts were never in scope of any audit conducted by the Omniscia team and thus are considered to be unaudited code. 

 While it may have been BonqDAO had the vulnerability, AllianceBlock has suffered significant collateral damage from this incident. 

 The sell-off of Bonq users' liquidated ALBT caused its price to dump up to ~75% following the attack. AllianceBlock have stated they will reissue the token and airdrop to users based on a Snapshot from before the hack.

 Bonq’s Euro stablecoin, BEUR , has dropped to approximately 25% below its peg and the price of the DAO’s token, BNQ , has also taken a hit of over 30%.

 AllianceBlock may not be at fault for the vulnerability, but perhaps they need to work on their due diligence. 

 It may not be the most exciting part of DeFi, but it’s surely amongst the most important.

 If AllianceBlock wants to achieve their aims of “ seamlessly bring[ing] DeFi and TradFi together ”, maybe they should take a more TradFi approach to due diligence.

 But it looks like it may already be too late for Bonq. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

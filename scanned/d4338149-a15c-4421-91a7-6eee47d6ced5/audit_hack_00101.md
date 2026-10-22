# [C] Euler Finance exploit: Against the backdrop of a banking meltdown and stablecoin crisis, one of DeFi’s most well-established lending protocols, Euler Finance, was struck a ~

## Summary
Severity: Critical
Target: Euler Finance
Loss: $197,000,000
Published: 03/13/2023
Source: https://rekt.news/euler-rekt
Type: rekt-postmortem

## Details
## Euler Finance - REKT

 Tuesday, March 14, 2023 Euler Finance - REKT 

 read this article also in : zh 

 Just as things were looking up… 

 Against the backdrop of a banking meltdown and stablecoin crisis, one of DeFi’s most well-established lending protocols, Euler Finance, was struck a ~$200M blow. 

 As USDC was creeping back towards its peg, Peckshield raised the alarm . 

 Euler Labs quickly acknowledged the exploit, stating they were “ working with security professionals and law enforcement ”.

 As the situation developed , the losses began to mount. A total of $197M in ETH, WBTC, USDC and DAI were taken, placing Euler at number 6 on the leaderboard . Euler’s TVL dropped from $264M to just $10M.

 Any hopes of a whitehat were quickly put to bed ; an associated address had previously been used to exploit BSC-based EPMAX before depositing the proceeds to Tornado Cash.

 How did it go so wrong? 

 Credit: _ FrankResearcher , Omniscia ,

 Lending on Euler is managed via eTokens (collateral) and dTokens (debt), with liquidations triggered when a user has more dTokens than eTokens. 

 The exploited vulnerability involved the little-used donateToReserves function which was incorporated into Euler via EIP14 last year. donateToReserves allows users to send eTokens to directly to Euler reserves, however does not contain a check on the health of the user’s position.

 The hacker took advantage of this by using two contracts, one of which would incur bad debt via donateToReserves, and the other would act as liquidator. 

 Using flash-loaned funds and Euler’s leverage system to create a large, underwater position on one contract, the liquidator contract could obtain the inflated eToken collateral at a discount, and withdraw into the underlying assets.

 Omniscia, one of Euler’s six auditors , published a detailed post-mortem , summing up the issue as follows:

 The attack ultimately arose from an incorrect donation mechanism and did not account for the donator’s debt health, permitting them to create an unbacked DToken debt that will never be liquidated.

 Attacker’s address (where funds remain): 0xb66cd966670d962c227b3eaba30a872dbfb995db 

 Example tx (DAI): 0xc310a0af… 

 SlowMist provided a summary of the addresses and transactions involved: total losses comprised 86k in ETH derivatives ($134.6M), 849 WBTC ($18.6M), 34M USDC, 8.9M DAI. 

 Auditors and smart contract insurance protocol Sherlock has taken responsibility for missing the vulnerability in their review of EIP-14 last year, and will pay a claim of $4.5M to Euler.

 Euler reached out to the attacker’s address via tx input data:

 We understand that you are responsible for this morning's attack on the Euler platform. We are writing to see whether you would be open to speaking with us about any potential next steps.

 But with some funds having been sent to Tornado via a pass-through address in what seems like a test, the prospects of returned funds aren’t looking good… 

 Given Euler’s high-profile and stable reputation, many other DeFi organisations had funds tied up in the protocol. 

 The fact that so many other projects chose to integrate with Euler is a testament to just how shocking this exploit has been for the community. And many have reached out in support of the Euler team.

 In addition to Euler itself (whose token, EUL , fell over 50%), the fallout affected the following projects: 

 Angle Protocol (over $17M of agEUR collateral, ANGLE down over 50%)

 Balancer ($11.9M of bbeUSD)

 Temple DAO ($5M, TEMPLE down 30%)

 Idle DAO (~$5M)

 Swissborg ($2.6M in ETH and $1.7M of USDT)

 Yield Protocol ($1.5M)

 Yearn ($1.38M of indirect exposure, losses to be covered by Treasury)

 Inverse Finance ($800k)

 And others 

 DeFi’s composability allows us to build interesting, automated and lucrative money legos in a way that traditional finance could never pull off. 

 When things go wrong, however, there’s no stopping the on-chain reaction. 

 The last few days have shown the necessity of a resilient alternative in an increasingly delicate global economy.

 Spurred on by disasters such as this, we continue to build out robust architecture, laying ever-stronger foundations for DeFi's future.

 But in the meantime… is anywhere truly safe? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

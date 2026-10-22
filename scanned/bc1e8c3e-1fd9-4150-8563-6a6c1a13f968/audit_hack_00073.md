# [H] Crema Finance exploit: Crema Finance , a concentrated liquidity AMM on Solana, was exploited into issuing millions in excess LP fees

## Summary
Severity: High
Target: Crema Finance
Loss: $8,800,000
Published: 07/02/2022
Source: https://rekt.news/crema-finance-rekt
Type: rekt-postmortem

## Details
## Crema Finance - REKT

 Monday, July 4, 2022 Crema Finance - REKT 

 read this article also in : zh 

 ~$8.8M skimmed off the top. 
 Crema Finance , a concentrated liquidity AMM on Solana, was exploited into issuing millions in excess LP fees. 

 The theft was announced by the team on Sunday at 04:07 UTC, though the attack took place the day before.

 Given that the same vulnerability was spotted by auditors in a different method, this one will be sure to leave a bitter taste for the Crema team. 

 Credit: Crema Finance , PierreArowana 

 The attack was made possible due to faulty owner validation on one of the protocol’s accounts storing price tick data. These data are used by Crema to calculate LP fees. 

 The hacker created a false tick account, with fake data, and used flash loans to add liquidity to the protocol. They could then withdraw the liquidity and claim the fees they were “owed” according to their own contract’s data.

 The proceeds were swapped to 69422.9 SOL and 6,497,738 USDCet (which was bridged to Ethereum and swapped for ETH) and remain in the hacker’s SOL and ETH addresses.

 Exploiter’s SOL address: Esmx2QjmDZMjJ15yBJ2nhqisjEt7Gqro4jSkofdoVsvY 

 Exploiter’s ETH address: 0x8021b2962dB803b73Aa874030B0B42c202E8458F 

 The Crema team have reached out to the exploiter in Solana transaction data, offering a whitehat bounty of $800k valid for 72 hours.

 ”To the Crema hacker: Your addresses on both Solana and Ethereum have been blacklisted and all eyes are on you right now. You have 72h from now to consider becoming a white hat and keeping 800k USD as the bounty. And transfer remaining funds back to our contract-update-authority address (DR1tLcKEmiNFxF5dxgdWCANdeBMNu9FjuHur2i4vAPHV) . Otherwise the police and legal force will officially get involved and there will be endless tracing waiting for you”

 Bramah Systems’s audit identified the same vulnerability in the Crema’s swap method (p. 7), which was fixed, but the issue also existed in the claim method, where it was not picked up. 

 The lack of sufficient validation has been the root cause of other high profile attacks on Solana this year.

 In the case of Wormhole , faulty signature verification across the bridge led to the loss of $326M, and Cashio suffered a loss of ~$48M due to incomplete validation of LP tokens used for collateral.

 The froth has gone from the markets, but can Crema Finance remain? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

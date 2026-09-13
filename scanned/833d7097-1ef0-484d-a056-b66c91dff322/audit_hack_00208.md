# [C] Qubit Finance exploit: Qubit Finance , a BSC-based lending protocol launched by the team behind repeat offender PancakeBunny, has fallen victim to an $80M exploit

## Summary
Severity: Critical
Target: Qubit Finance
Loss: $80,000,000
Published: 01/28/2022
Source: https://rekt.news/qubit-rekt
Type: rekt-postmortem

## Details
## Qubit Finance - REKT

 Friday, January 28, 2022 Qubit Finance - BSC - REKT 

 read this article also in : zh 

 In other news… 

 Qubit Finance , a BSC-based lending protocol launched by the team behind repeat offender PancakeBunny, has fallen victim to an $80M exploit.

 That’s number seven on our leaderboard .

 But will anyone remember this next week? 

 Qubit allows for cross-chain collateralisation , locking assets on Ethereum to borrow against on BSC via the QBridge deposit function.

 The attacker took advantage of a logic bug in the code which made xETH available for use on BSC without having deposited ETH on Ethereum.

 The attacker’s Ethereum address was funded from Tornado Cash shortly before the exploit commenced at approximately 21:30 PM +UTC on January 27th 2022.

 From the Qubit team’s post-mortem :

 1. The attacker called the QBridge deposit function on the ethereum network, which calls the deposit function QBridgeHandler.

 2. QBridgeHandler should receive the WETH token, which is the original tokenAddress, and if the person who performed the tx does not have a WETH token, the transfer should not occur.

 3. tokenAddress.safeTransferFrom(depositer, address(this), amount);

 4. In the code above, tokenAddress is 0, so safeTransferFrom didn’t fail and the deposit function ended normally regardless of the amount value.

 5. Additionally, tokenAddress was the WETH address before depositETH was added, but as depositETH is added, it is replaced with the zero address that is the tokenAddress of ETH.

 6. In summary, the deposit function was a function that should not be used after depositETH was newly developed, but it remained in the contract.

 According to Certik’s analysis :

 One of the root causes of the vulnerability was the fact that tokenAddress.safeTransferFrom() does not revert when the tokenAddress is the zero (null) address (0x0…000). 

 Despite not having locked any ETH in the Ethereum contract, the attacker’s BSC address now had access to 77,162 qXETH ($185 million) to use as collateral against loans on Qubit.

 They used this collateral to borrow WETH, BTC-B, USD stablecoins, and CAKE, BUNNY, and MDX before swapping everything for a total of 200k BNB (~$80M), which remains in the BSC address .

 According to the Qubit docs, the cross-chain collateral feature was audited in Dec 2021. 

 the whole X-Collateral feature (including contracts and scripts) has been audited by Theori, a professional auditing firm. The audit result is published here . 

 The project has a max bounty of $250k on Immunefi , but the Qubit team seems prepared to negotiate .

 Back in May 2021, we were gifted 100k DAI by the Pancake Bunny hacker.

 We returned the funds, and told the team “not to lose it this time”, yet here we are again.

 Our donation address is listed below.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] LiFi/Jumper exploit: LiFi protocol lost $9.73M to an attack draining addresses that had previously approved infinite permissions to the protocol's contracts across multipl

## Summary
Severity: High
Target: LiFi/Jumper
Loss: $9,730,000
Published: 07/16/2024
Source: https://rekt.news/lifi-jumper-rekt
Type: rekt-postmortem

## Details
## LiFi/Jumper - Rekt

 Tuesday, July 16, 2024 LiFi Protocol - Jumper Exchange - REKT 

 read this article also in : zh 

 Infinite approvals... the ultimate leap of faith strikes again. 

 LiFi protocol lost $9.73M to an attack draining addresses that had previously approved infinite permissions to the protocol's contracts across multiple chains. 

 Shortly after the alarm was raised by security firm CertiK , the LiFi team acknowledged the hack roughly an hour later .

 Jumper Exchange, which is powered by LiFi's services, also informed their users about the exploit and appears to be unaffected as of now .

 Both LiFi and Jumper urged users to check whether their addresses were affected and revoke approvals via revoke.cash .

 What's more concerning is that LiFi suffered from an almost identical exploit back in March 2022 , losing $600K from 29 wallets. 

 Why did a known bug make it to production on a live protocol... again? 

 Credit: CertiK , Nick L. Franklin , Peckshield , LiFi , Jumper Exchange , Rivanorth 
 Five days is all it took for history to repeat itself. 

 On July 11th, a new contract facet was added to the LiFi protocol.

 This new contract contained a vulnerable function that lacked proper validation.

 As Nick L. Franklin pointed out that the attack was due to a lack of validation in the "swap" function of the new contract facet added to the protocol. 

 The vulnerable contract failed to properly check the call target and call data, allowing an exploiter to perform a "call injection" attack.

 This enabled the attacker to execute arbitrary functions using the permissions granted to the LiFi contract. 

 Because of this, users who approved the contract for infinite approvals lost their tokens.

 LiFi router set this implementation recently: 

 Attacker's address: 
 0x8B3Cb6Bf982798fba233Bca56749e22EEc42DcF3 

 Affected contract addresses: 
 EVM Chains: 0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae 
 zkSync: 0x341e94069f53234fE6DabeF707aD424830525715 
 Linea: 0xDE1E598b81620773454588B85D6b5D4eEC32573e 
 Metis: 0x24ca98fB6972F5eE05f0dB00595c7f68D9FaFd68 

 Funds stolen include USDT, USDC, and DAI totalling approximately $9.73M, which were subsequently swapped for 2,857 ETH.

 The stolen assets have been distributed to multiple wallets controlled by the attacker.

 As the $3.3M Socket protocol hack on January 16th shows, cross-chain bridges and aggregators continue to be prime targets for blackhats. 

 Let me know if this sounds familiar? 

 The Attacker targeted wallets that had granted infinite approvals to Socket contracts exploiting a recently added route to their bridging contract.

 Peckshield provided some further analysis on the hack and seen a direct parallel to the previous attack on LiFi: 

 In the post-mortem of the previous exploit , LiFi stated “We then implemented a whitelist to only allow calls to approved DEXs. Our contract was upgraded to include this new whitelist functionality, and swaps were reenabled. On top of that, we have disabled infinite approvals by default.” 

 No word on the most recent contract facet being audited.

 Looks like this fell between the cracks, proving once again that in DeFi, yesterday's patch is tomorrow's exploit. 

 With millions at stake, how many more "infinite approvals" will it take before users stop playing Russian roulette with their assets? 

 Infinite approvals: The gift that keeps on grifting. 

 Despite LiFi's response that only wallets affected were set to infinite approvals and represented only a very small number of users, the magnitude of the loss suggests otherwise. 

 It's hard to believe that so many users would be vulnerable if infinite approvals weren't commonplace.

 With nearly $10M stolen, this will have been a costly lesson in approvals hygiene for many.

 Without a regular revoking detox using a tool such as revoke.cash , token approvals sit waiting for a live (or forgotten) project to be exploited. 

 However, all this could have simply been avoided by not making risky, unaudited upgrades to an existing protocol contract.

 Infinite approvals to upgradeable contracts should come with warnings by every wallet

 Maybe it's time to start questioning those "infinite" permissions. 

 Have you checked your approvals lately? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

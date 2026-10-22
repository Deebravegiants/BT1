# [C] StableMagnet exploit: They told us it was going to happen, then it did

## Summary
Severity: Critical
Target: StableMagnet
Loss: $27,000,000
Published: 06/23/2021
Source: https://rekt.news/stablemagnet-rekt
Type: rekt-postmortem

## Details
## StableMagnet - REKT

 Thursday, June 24, 2021 StableMagnet - BSC - REKT 

 read this article also in : zh 

 They told us it was going to happen, then it did. 
 A few hours before the attack, we received a direct message from an anonymous source suggesting that StableMagnet would rugpull.

 We couldn’t verify the claims, and therefore our hands were tied. 

 If we had made a public warning and the accusations had been false, we would have caused FUD and potentially damaged an innocent project.

 There was no scope to whitehack the funds, so all we could do was wait.

 Now there’s $27 million gone, and more due to be stolen from the wallets of those who have not yet revoked permissions to StableMagnet.

 Users can use the BSC Token Approval Checker to revoke these permissions. 

 We were unable to stop this attack, and that knowledge is not easy to accept. However, the information we received correlates with some of our previously held suspicions. 

 Techrate audits are not to be trusted. 

 The rug pull started with this transaction: 

 An initial $22.2 million in stablecoins were taken from the StableMagnet 3Pool via an unverified source code. 

 This figure is now $27M and rising. 

 As stated by Rugdoc: 

 Etherscan and BSCScan explorers do not verify linked library source code.

 This allows the exploiter to deploy a completely different library than the one in the source code.

 The unverified SwapUtil library did not only contain code to drain all pairs, it also contained code to transfer more tokens to everyone who had approved StableMagnet.

 SwapUtils library containing the exploit: 0xE25d05777BB4bD0FD0Ca1297C434e612803eaA9a 

 Other protocols which are still in operation, such as Dopple and StableGaj are based upon the same code, and their SwapUtils libraries are also unverfied.

 The stolen funds were split between multiple addresses and deposited to Binance in order to switch to the Ethereum blockchain, then quickly withdrawn and the centralised USDT exchanged for decentralised DAI. 

 These attackers had planned their escape route.

 Is the Binance KYC process faulty, or do Binance care less about enforcing the law than they would have us believe? 

 BUSD sent to Binance hot wallet: 0x2bac04457e5de654cf1600b803e714c2c3fb96d7 

 Tether received on ETH chain: 0xDF5B180c0734fC448BE30B7FF2c5bFc262bDEF26 

 Tether changed to DAI: 0xe5daac909a3205f99d370bc2b32b1810a4912a07 

 This pattern has been replicated across multiple addresses. 

 Could this be the rug that keeps on rugging? 

 At one point, there were over 1000 users with non-zero allowances on the rugpulled StableMagnet.

 With an initial entry at number 8, this case is set to keep on climbing the rekt leaderboard as we uncover more of the story and the wallets of unsuspecting users continue to be drained.

 This is not the first time that this group has rugpulled, but this time they’ve left us some clues. 

 The other information that was given to us by our anonymous source is given more authenticity following the events at StableMagnet. 

 They told us that the same group is responsible for multiple recent rugpulls, suggesting that Moon Here token , and Wen Moon token were also carried out by the same bad actors.

 They also told us that “ Techrate audited the Github , but not the deployed contract” 

 We know that Techrate was alerted to this rugpull, and that they took no action. A quick glance through the list of projects that they are involved with will give you a good idea of the kind of quality you can expect with a Techrate audited project.

 Why should we expect them to point out the problem, rather than let it slide and come back to it later when they are wearing their black hat? 

 In a space and time where trust is already at a minimum, you would hope you could look to audit companies for some security. 

 However, this is not the first incident in which the auditor becomes the number one suspect.

 We know of at least two major hacks in which the protocol is working to prove that they were attacked by their auditor. Investigations are ongoing. 

 This has been one of the more sinister rug pulls that we have documented. A known group of attackers stealing not only from their scam protocol, but also directly from users wallets, then fleeing to the decentralised protection of DAI.

 Don’t trust an auditor to DYOR. 

 If you enjoy our work, please donate to our Gitcoin grant. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

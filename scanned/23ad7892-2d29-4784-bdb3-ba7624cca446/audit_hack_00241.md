# [H] Socket exploit: Infinite approvals… the ultimate leap of faith

## Summary
Severity: High
Target: Socket
Loss: $3,300,000
Published: 01/16/2024
Source: https://rekt.news/socket-rekt
Type: rekt-postmortem

## Details
## Socket - REKT

 Wednesday, January 17, 2024 Socket - Bungee - Bridge - REKT 

 read this article also in : 

 Infinite approvals… the ultimate leap of faith. 

 Socket’s Bungee bridge lost $3.3M yesterday to an attack draining addresses that had previously approved the SocketGateway contract on Ethereum. 

 Shortly after the alarm was raised , the team acknowledged the hack, having patched the vulnerability just 14 minutes after the attack began .

 Wallet provider Rainbow also informed their users, as Socket’s contracts are used by the in-app bridging feature. They urged users to check whether their address was affected and revoke approvals via RevokeCash’s dedicated tool .

 As the over $80M NYE attack on Orbit shows, bridges continue to be a prime target for blackhats, and must be subject to the highest levels of scrutiny whenever any changes are made. 

 Why did a known bug make it to production on a live bridge? 

 Credit: qckhp , Peckshield , Beosin 

 The attack was due to a lack of validation of user input contained in a new route added to the bridging contract three days prior to the exploit. 

 The vulnerable route’s contract itself neglects to validate the swapExtraData parameter, allowing an exploiter to inject a transferFrom call, and send approved assets from victim addresses to their attack contract.

 As Beosin points out :

 It did not consider the case where the caller transfers in 0 WETH, allowing the caller to specify other functions in the call and still pass the balance check.

 Attacker’s address: 0x50df5a2217588772471b84adbbe4194a2ed39066 

 SocketGateway contract: 0x3a23f943181408eac424116af7b7790c94cb97a5 

 Socket contracts have audits by both Peckshield and Consensys Diligence . However, given that the new route was added just three days prior to the exploit, neither audit examined the vulnerable code.

 Funds stolen include ETH, MATIC, WBTC, WETH and DAI totalling approximately $3.3M. 

 The stolen assets remain in the attacker's address, which has received a message threatening to dox the attacker if not paid off:

 100 ETH and I'll throw away the timing analysis routing through FixedFloat that doxxes you. After 6 hours I go to Zach. Act swiftly.

 Infinite approvals strike again. 

 Despite Bungee’s response that “ Bungee doesn't request infinite approvals by default ”, other protocols which route via the affected contract must subscribe to the UI before security mindset.

 Otherwise, it’s hard to believe that so many users would be vulnerable. 

 With the biggest loss at over $600K and the five hardest-hit victims each losing over $100K, this will have been a costly lesson in approvals hygiene for some. 

 Without a regular revoking detox, token approvals sit waiting for a live ( or forgotten ) project to be exploited. And given that tokens are stolen directly from users’ wallets, there’s no need to have any funds deposited to fall victim.

 However, all this could have simply been avoided by not making risky, unaudited upgrades to an existing bridge contract. 

 Have you checked your approvals lately, anon? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [M] Unibot exploit: Unibot users woke up to seasonally scary news this morning

## Summary
Severity: Medium
Target: Unibot
Loss: $640,000
Published: 10/31/2023
Source: https://rekt.news/unibot-rekt
Type: rekt-postmortem

## Details
## Unibot - REKT

 Tuesday, October 31, 2023 Unibot - Trading bot - REKT 

 read this article also in : 

 Unibot users woke up to seasonally scary news this morning. 

 The trading bot’s brand new router was exploited to drain at least $640k from users who had approved the contract. 

 An hour after Peckshield raised the alarm , the team’s response gave the impression that the exploit was over:

 We experienced a token approval exploit from our new router and have paused our router to contain the issue.

 Any funds lost due to the bug on our new router will be compensated. Your keys and wallets are safe.

 However, copycats deployed cloned exploit contracts and continued to drain funds after the official announcement.

 Any user with existing approvals to the new router contract remained vulnerable. 

 Why didn’t the team warn users to revoke their approvals? 

 Credit: Beosin , BlockSec 

 Unibot’s new router contract , which had been deployed on Saturday and remains unverified on Etherscan, contained a vulnerability which allows an attacker to insert a transferFrom() call to drained approved tokens directly from Unibot user wallets.

 Any users who had approved the new router to spend tokens, and not yet revoked , is a potential victim. 

 Revoke approvals for the router contract address: 0x126c9FbaB3A2FCA24eDfd17322E71a5e36E91865 

 Specifically, BlockSec explained that:

 As the code is not open-sourced, we suspect that there is a lack of input validation of the function 0xb2bd16ab in the 0x126c contract, which allows an arbitrary call. Therefore, an attacker could invoke 'transferFrom' to transfer out tokens approved to the contract.

 Beosin provided the following diagram of the vulnerable code:

 While the original exploiter has been inactive since sending 355 ETH ($640k) of profits to Tornado Cash, there have been reports of copycat attackers deploying contracts to replicate the exploit. 

 Exploiter address: [0x413e4fb75c300b92fec12d7c44e4c0b4faab4d04] ( https://etherscan.io/address/0x413e4fb75c300b92fec12d7c44e4c0b4faab4d04 )

 Example attack tx: 0xcbe521ae… 

 The attack looks to be identical to one that hit Maestro, another TG trading bot, for ~$500k last week. 

 However, Maestro’s response was quick and clear, even refunding users with more than they had lost. Hopefully refunds for today’s victims will be easily budgeted for after the volume they created.

 But it seems bizarre that Unibot, a team working on a such a similar product, wouldn’t have double-checked their new router code for the same vulnerability after such recent incident. 

 In contrast, some responses from the Unibot team seemed to diminish the risk, potentially leading to further losses.

 Ouch. 

 TG trading bots, like the recent SocialFi ponzi boom, sacrifice security for convenience. 

 While this incident did not involve compromised keys, trusting your wallet to a closed-source project is exactly the kind of behaviour we’re continually warned about.

 And as today’s incident ( as well as LastPass , and StarsArena ) shows, these UX tradeoffs sometimes result in costly lessons about trust.

 Will we ever learn? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

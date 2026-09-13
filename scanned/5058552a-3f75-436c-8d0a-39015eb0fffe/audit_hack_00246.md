# [H] Super Sushi Samurai exploit: While you were busy playing with your food, someone stole your lunch

## Summary
Severity: High
Target: Super Sushi Samurai
Loss: $4,800,000
Published: 03/21/2024
Source: https://rekt.news/sss-rekt
Type: rekt-postmortem

## Details
## Super Sushi Samurai - REKT

 Friday, March 22, 2024 Super Sushi Samurai - REKT 

 read this article also in : zh 

 While you were busy playing with your food, someone stole your lunch. 

 Blast L2-based game Super Sushi Samurai's LP drained $4.8m in contract bug exploit shortly after its launch, and the price dropped 99.9%. 

 Spreek sounded the alarm around 14:00 UTC and the Super Sushi Samurai team responded within minutes , saying that they were pausing token transfers and investigating.

 Half an hour after getting sliced and diced, the Super Sushi Samurai team commented further on the exploit:

 We have been exploited, it's mint related. We are still looking into the code. Tokens were minted and sold into the LP. 

 Gamma Strategies was hit with a similar mint exploit earlier this year, resulting in a similar loss on Arbitrum.

 Super Sushi Samurai’s code was audited, but failed to identify the infinite mint exploit. 

 Will some of these protocols and auditing firms ever get this right or keep dropping the ball? 

 Credit: Spreek , Super Sushi Samurai , Coffeexcoin , Sudo 
 The Super Sushi Samurai LP was drained due to a critical bug in the token contract that allowed users to double their token balance simply by transferring the entire balance to their own address.

 The issue stemmed from a coding oversight in the contract's transfer function. When transferring tokens, the contract subtracts the amount from the sender's balance before adding it to the recipient's balance. However, if the sender and recipient are the same address, the contract fails to account for the deducted amount, causing the balance to double instead of remaining unchanged. 

 This exploitable loophole enabled the attacker to repeatedly double their balance and ultimately sell the artificially inflated holdings, resulting in a $4.8M loss for the project. 

 It only took the attacker around an hour to flip $35 into $4.6M . Quite a profit, isn’t it?

Attacker Contract:
 0xDed85d83Bf06069c0bD5AA792234b5015D5410A9 
 Attacker Address: 0x6a89a8c67b5066d59bf4d81d59f70c3976facd0a 

 Attack Transaction 1: 0x80012bf784b83baaf28f5549a9f233cae5f70be7afcd8f594dc757d431ed93c4 

 Attack Transaction 2: 0x62e6b906bb5aafdc57c72cd13e20a18d2de3a4a757cd2f24fde6003ce5c9f2c6 

 Attack Transaction 3: 0xac3400e3d536ac23c10fdd2c06e1faf8d5de5b797df8433e9b5ab74b102a4e35 

 However, the funds may not entirely be lost. The person who drained the funds sent a message saying that it was a whitehat rescue hack . They provided details for contacting them and said that users should get reimbursed. The project said it had reached out to the exploiter. 

 Verichains was responsible for the audit and missed the exploit.They let the contract go live with an infinite mint exploit.

 Another audit, another exploit. Is it time to start auditing the auditing firms? 

 In the aftermath of the Super Sushi Samurai exploit, it's crucial for the crypto community to reflect on the importance of thorough security audits and the role of auditing firms in ensuring the safety of users' funds. 
 The incident raises concerns about the effectiveness of current auditing practices, given that the contract was audited by Verichains but still went live with an infinite mint exploit. 

 This event serves as a reminder for both projects and users to remain vigilant and ensure the highest security standards are being met.

 Collaborative efforts should focus on improving smart contract development standards and establishing industry-wide best practices.

 It may be time for the industry to consider stricter auditing requirements and establish better mechanisms for identifying and addressing vulnerabilities in smart contracts. 

 By working together to develop more robust security measures and promoting transparency in the auditing process, the crypto community can foster an environment where users feel confident in the security of their investments.

 Moreover, the Super Sushi Samurai incident should serve as a catalyst for reevaluating the relationships between projects and auditing firms.

 While the outcome of the Super Sushi Samurai incident remains uncertain, with the exploiter claiming to be a whitehat hacker and offering to reimburse affected users, it provides an opportunity to reevaluate and improve the overall security landscape. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

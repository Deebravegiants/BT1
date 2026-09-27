# [C] WazirX exploit: WazirX, India's leading crypto exchange, took a massive $235 million hit when it's Safe multisig wallet crumbled under a devastating breach

## Summary
Severity: Critical
Target: WazirX
Loss: $235,000,000
Published: 07/18/2024
Source: https://rekt.news/wazirx-rekt
Type: rekt-postmortem

## Details
## WazirX - Rekt

 Thursday, July 18, 2024 WazirX Protocol - REKT 

 read this article also in : 

 WazirX, India's leading crypto exchange, took a massive $235 million hit when it's Safe multisig wallet crumbled under a devastating breach. 

 Cyvers sounded the alarm shortly after the attack, detecting multiple suspicious transactions being funded by Tornado Cash making moves on the platform. 

 They attempted to contact WazirX during the explicit, but it was too late, as the attacker was already swapping the stolen tokens to ETH and making their exit.

 Roughly half an hour later, WazirX confirmed the security breach and that they were pausing withdrawals.

 WazirX is sliding into number 7 on the infamous Rekt Leaderboard , right behind this year’s biggest hack, so far, DMM Bitcoin , which lost $304 million at the end of May.

 DMM Bitcoin was another centralized exchange that fell victim to a multisig compromise. 

 How many times do we need to be reminded of not your keys, not your crypto? 

 Credit: Cyvers , WazirX , Mudit Gupta , ZachXBT , Arkham Intel 
 The WazirX hack was a masterclass in patience and deception. 

 According to a technical breakdown provided by Mudit Gupta , the attackers began laying the groundwork at least 8 days before the main event, conducting small test transactions to set the stage.

 Their target? WazirX's multisig wallet, which had six signatories, five from WazirX and one from Liminal, their custody provider. This was confirmed by WazirX in their preliminary report of the exploit.

 Instead of a straightforward drain, the hackers opted for a more insidious approach. They set out to upgrade the multisig wallet to a malicious version under their control. 

 To achieve this, they needed to overcome WazirX's security measures, which included Ledger Hardware Wallets for signatories and a whitelist policy for destination addresses. 

 The attackers likely compromised two of the four required private keys directly. For the remaining two, they employed signature phishing, tricking signers into approving what appeared to be a normal USDT transfer .

 This deception extended to Liminal's interface, where WazirX suspects a discrepancy between the displayed data and the actual transaction contents allowed the payload to be replaced.

 Minutes before the hack, a legitimate USDT transfer failed, a red flag that went unnoticed. 

 Two of the four signatures were actually for upgrading the safe to the malicious contract, not for the USDT transfer.

 With all pieces in place, the hackers executed their exploit. 

 Using the two compromised keys and the two phished signatures, they successfully upgraded the multisig to their malicious contract. 

 Critically, one of the phished signatures came from Liminal Custody, the co-signer responsible for final checks.

 This suggests a significant failure in Liminal's verification process, a vulnerability the attackers exploited to devastating effect.

 With the upgrade complete, the attackers gained full control of the wallet, allowing them to drain funds at will. 

 ZachXBT's investigation revealed a complex trail of transactions , broken down into a timeline as follows... 

 July 8th: 

 A ChangeNOW hot wallet sent two transactions to this address: 
 0xC891b507A7c109179d38E2Cb4DE6CD8Dc70D2ad4 

 2 Transactions: 

 0.36 ETH: 0xc2fdc27f98cf02c2da2a180fa35824dc365c63795e7a7ce12ba88c1e06edd4f7 

 0.66 ETH: 0xa62685d8a8b39920e957e0aaf56d527aec6d65bc9323d3d219e11f44e150e224 

 Timing analysis suggests these funds originated from Bitcoin transactions: 
 53795dd1629026c2f92a87d5cd2447736f1afc9cae71262f3af9e62a4ac83b92 

 ddfd189125ce88c622ec2453b2e9f2dbe5c5c0931f16e3389eac4976c757e5b9 

 Address 0xc687 received 1 ETH from Tornado Cash: 

 0xe3b4cf64e0fc25fafb10d226984b18addc038879ed77f730abbed4737db6a5fc 

 The matching 1 ETH deposit to Tornado Cash was made 9 hours before: 

 0x87c01ca1f56ef3663651b05cd8ebcf133281c5fdd0ef1016f83a16a862c4a235 

 July 9th: 

 Addresses 0xc687 and 0xc891 transferred funds to each other, potentially compromising their Tornado Cash privacy. 

 Transaction 1: 

 0x5a7e3b2b2425b17ab8afe5aee06245e30d935598b16f1c06958cac50d8fe7948 

 Transaction 2: 

 0xd43c39187f1fdd904b6e1b4da53a1c9bb7ca19a0fc7adcb0dfbbbe732c244f33 

 July 10th: 

 Six deposits of 0.1 ETH each were made to Tornado Cash from this address: 
 0xc6873ce725229099caf5ac6078f30f48ec6c7e2e 

 The main attack address received 6 x 0.1 ETH from Tornado Cash: 

 0x6EeDF92Fb92Dd68a270c3205e96DCCc527728066 

 The attack address began test transactions involving ETH, SHIB and USDT with the 0x09b multisig: 

 ETH Transaction: 
 0xc6cb4c0726efd4f9015924e7d528e19362c01e8d3a4e77bf78f073cf963a2bc2 

 SHIB Transaction: 
 0x1455f995980056cf1ddb5bba4a848800b0770caadc11e259a815562721fc2bcd 

 USDT Transaction: 
 0xc850b252ab32d80203991c9b5359205e917c94c94d3c47d04d8b153453b1e2b2

 July 18th (Attack Day): 

 The attack was executed on the WazirX Wallet: 0x27fD43BABfbe83a81d14665b1a6fB8030A60C9b4 

 This address was used to trigger smart contract calls: 0x6EeDF92Fb92Dd68a270c3205e96DCCc527728066 

 This address was used to drain funds: 
 0x04b21735E93Fa3f8df70e2Da89e6922616891a88 

 Flow of Funds: 

 In a twist that would make a spy novelist proud, ZachXBT solved an Arkham bounty by identifying a KYC exchange deposit made by the WazirX hacker. 

 This intricate web of transactions reveals the meticulous planning and execution behind the WazirX hack.

 The attackers' use of privacy tools, test transactions, and multiple addresses demonstrates a level of sophistication not seen in most crypto heists.

 Mudit Gupta made a good point in his analysis, “It's a very methodical and organized attack, pointing towards DPRK as the hacker.” 

 This has yet to be confirmed, but you never know…

 Could this be another case of state-sponsored crypto theft? 

 This $235 million heist not only shakes user confidence but also raises questions about the efficacy of current custody solutions and multisig implementations. 

 In a world where even the most robust security measures can be bypassed, is entrusting large sums to any single entity, no matter how reputable, a risk worth taking? 

 The rise of sophisticated, possibly state-sponsored attacks adds a chilling new dimension to an already treacherous landscape.

 With data breaches becoming the norm, the rise of phishing attacks and compromised private keys and multisig a rising concern lately.

 We have to ask, where is it safe to store our funds?

 The short answer is obviously not centralized exchanges. 

 Is the only path forward a world where every user becomes their own bank, guardian and last line of defense? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

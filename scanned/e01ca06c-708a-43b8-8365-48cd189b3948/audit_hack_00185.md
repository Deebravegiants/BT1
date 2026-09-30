# [H] OKX DEX exploit: OKX’s decentralised exchange aggregator has fallen victim to one of the oldest tricks in the book, losing $2.7M to a private key compromise

## Summary
Severity: High
Target: OKX DEX
Loss: $2,700,000
Published: 12/12/2023
Source: https://rekt.news/okx-dex-rekt
Type: rekt-postmortem

## Details
## OKX DEX - REKT

 Wednesday, December 13, 2023 OKX - REKT 

 read this article also in : 

 CeDeFi strikes again. 

 OKX’s decentralised exchange aggregator has fallen victim to one of the oldest tricks in the book, losing $2.7M to a private key compromise. 

 The losses were caused by a compromised proxy contract, which was upgraded and used to steal funds from users who had approved it.

 After community reports of funds going missing, Slowmist raised the alarm . 

 An official acknowledgement came shortly after, stating that the affected contract was a deprecated version, and had now been secured. 

 But if the contract was deprecated, why did they wait until it got rekt? 

 Credit: SlowMist 

 Although OKX itself is a centralised exchange, it runs a DEX aggregator (featuring “ best-in-class security ”, apparently ) to help its more intrepid users seek out more niche opportunities on-chain. 

 According to SlowMist , the proxy admin of a trusted contract controlling OKX DEX trades was compromised. Then, shortly before midnight UTC, the implementation was upgraded in order to siphon user funds from addresses which had approved the proxy.

 The pattern is described as follows: 

 ...when users exchange, they authorize the TokenApprove contract, and the DEX contract transfers the user's tokens by calling the TokenApprove contract. The DEX contract has a claimTokens function that allows a trusted DEX Proxy to make calls, with its functionality being to invoke the claimTokens function of the TokenApprove contract to transfer tokens authorized by the user. The trusted DEX Proxy is managed by the Proxy Admin, and the Proxy Admin Owner can upgrade the DEX Proxy contract through the Proxy Admin.

 Once compromised: 

 ...the Proxy Admin Owner upgraded the DEX Proxy contract to a new implementation contract through the Proxy Admin. The new implementation contract's functionality is to directly call the claimTokens function of the DEX contract to transfer tokens. Subsequently, attackers began calling the DEX Proxy to steal tokens.

 Relevant addresses/txs: 

 DEX contract: 0x70cbb871e8f30fc8ce23609e9e0ea87b6b222f58 

 OKX DEX TokenApprove contract: 0x40aa958dd87fc8305b97f2ba922cddca374bcd7f 

 DEX Proxy: 0x55b35bf627944396f9950dd6bddadb5218110c76 

 Proxy Admin: 0x3c18F8554362c3F07Dc5476C3bBeB9Fdd6F6a500 

 Proxy Admin Owner: 0xc82Ea2afE1Fd1D61C4A12f5CeB3D7000f564F5C6 

 Upgrade Transactions: 0xc6a5a7bc… and 0x22ebd2… 

 Suspected Attacker [ funded via Tornado Cash]: 0xFacf375Af906f55453537ca31fFA99053A010239 

 Profit Address [holding $430k]:

 0x1F14E38666cDd8e8975f9acC09e24E9a28fbC42d 

 While SlowMist’s initial analysis put the losses at around $430k, PeckShield and Hacken traced a total of $2.7M stolen, adding the following addresses which received a total of 800 ETH ($1.7M) and $620k in stablecoins:

 0xa15fe801dd5fd31a684c444b6980dbaf0c78d5ad 

 0x22a2931cb2a7b782d65b2b5562829e84d941b0f0 

 0xfe55502a57f388a69602b2780071b759a520468f 

 0x48e3712c473364814ac8d87a2a70a9004a42e9a3 

 Private key compromises are often carried out by the experts , and have often led to heavy losses from CEXs, including Poloniex and HTX ( twice ), recently. 

 Last week we covered some of the latest phishing techniques, pointing out how even experienced users can find it hard to notice common scam methods, including address poisoning campaigns. 

 Fitting then, that today’s story shows how even professional security auditors can mistakenly copy/paste phishing addresses into their write-ups , after presumably misidentifying fake token transfer as a genuine 300 ETH dispersal.

 But CEXs like OKX are aimed at retail, not experts. 

 Are retail users really expected to know about trust assumptions around proxy implementations, or know to revoke deprecated contracts?

 Well that’s CeDeFi innovation for you… making sure you can get rekt by CEX private key leaks even on-chain. 

 OKX initially promised $370k to reimburse victims in their response, before moving on to more important topics .

 Will they cover the rest? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

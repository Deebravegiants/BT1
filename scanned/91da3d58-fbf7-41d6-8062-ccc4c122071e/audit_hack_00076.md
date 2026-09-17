# [M] Curve Finance exploit: Curve Finance’s principal front end, curve.fi , fell victim to a DNS hijacking yesterday , in which users were prompted to approve a malicious contrac

## Summary
Severity: Medium
Target: Curve Finance
Loss: $575,000
Published: 08/09/2022
Source: https://rekt.news/curve-finance-rekt
Type: rekt-postmortem

## Details
## Curve Finance - REKT

 Wednesday, August 10, 2022 Curve Finance - DNS hijack - REKT 

 read this article also in : zh 

 Curve Finance’s principal front end, curve.fi , fell victim to a DNS hijacking yesterday , in which users were prompted to approve a malicious contract. 

 Approximately $575k was stolen from users who approved, with proceeds being sent to CEXs and Tornado Cash. It seems OFAC’s sanctions don’t scare those who are already breaking the law…

 The exploit was not active on curve.exchange , the project's alternate UI, which the team directed users to while the incident was dealt with. The hacker’s mirrored site was taken down quickly, however some nameservers are still to be updated .

 This episode, and others like it, serve as stark reminders that web3 still runs on web2. 

 When even the backbone of DeFi is reliant on legacy infrastructure…

 …how decentralised can we claim to be? 

 As with other DNS hijacking events, identification of the exact cause falls to the service provider, and we must rely on their account of events, without being able to corroborate on-chain.

 So far, iwantmyname is yet to comment on exactly what led to the hijacking, but Curve believes that the underlying nameserver was compromised, rather than a vulnerability at the account level. 

 Curve Founder and CEO Michael Egorov confirmed his team's suspicions with rekt.news:

 Well for now I can say that dns registrar iwantmyname had their ns compromised

 No account hack

 Switched the ns

 Besides a good bunch of hacked money frozen by centralized services

 What could be done better.. we should try to go away from web2 things like dns tbh, that would be the best

 Further details provided here .

 All Curve users who interacted with the platform should revoke approvals to the malicious contract immediately: 

 0x9eb5f8e83359bb5013f3d8eee60bdce5654e8881 . 

 Attacker’s address: 0x50f9202e0f1c1577822bd67193960b213cd2f331 

 The stolen funds (340 ETH, or ~$575k, in total) have been deposited to CEXs FixedFloat (292 ETH of which 112 ETH have been frozen ) and Binance (20 ETH) as well as Tornado Cash (27.7 ETH)

 Currently, for the vast majority of users, DeFi is only as secure as the centrally-hosted front ends that they interact with. 

 As the battle-tested contracts which secure established protocols’ back end become gradually more robust, exploiters are increasingly targeting the front end. This vector leverages users’ trust in the project’s contracts whilst overlooking the security behind the UI.

 Without real decentralisation at every step, we will continue to see approval-harvesting attacks, such as those that have affected users of BadgerDAO , Mad Meerkat Finance and, most recently, the Namecheap breach which affected front ends of four DeFi protocols.

 For all the effort put into smart contract security, audits and decentralisation of governance powers, a project’s reputation can get still rekt through the fault of a web2 corporation.

 Aside from monitoring for any site changes , DeFi protocols (and more importantly, users) are stuck trusting another company’s security infrastructure and staff members .

 The next logical step is protocols hosting their Dapps via IPFS and ENS, cutting reliance on web2 DNS providers. 

 The vast majority of users are not interested in dealing directly with smart contracts; front end security should not be treated as an afterthought. 

 How much longer will web3 rely on web2? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Steadefi exploit: Steadefi lost $1.14M to a compromised deployer address on Monday

## Summary
Severity: High
Target: Steadefi
Loss: $1,140,000
Published: 08/07/2023
Source: https://rekt.news/steadefi-rekt
Type: rekt-postmortem

## Details
## Steadefi - REKT

 Tuesday, August 8, 2023 Steadefi - REKT 

 read this article also in : 

 Steady lads. 

 Steadefi lost $1.14M to a compromised deployer address on Monday. 

 Phishing or an inside job? 

 The yield farm on Arbitrum and Avalanche announced the exploit: 

 NOTICE: Steadefi has been exploited and all funds are currently at risk.

 The warning came with an on-chain bounty plea to the attacker (though a second message followed, due to a typo in the email provided for negotiation…).

 Taking inspiration from the bounty offered following the recent hack of Curve pools , the exploiter has a deadline to return 90% of the funds, keeping the rest as a bounty.

 After the deadline, the 10% bounty will be offered to the public as a reward for information leading to a conviction. 

 Could this a new industry standard for bounty payments? 

 And will it work? 

 Credit: Steadefi 

 According to Steadefi’s own announcement , the deployer address of the protocol was compromised.

 As the deployer was the owner of all of the platform’s vault contracts, the attacker was able to transfer ownership (for example, the USDC vault on Abritrum in this tx ) to their own address. From there, the exploiter:

 went on to take various owner-only actions such as allowing any wallet to be able to borrow any available funds from the lending vaults.

 The attack drained all funds available for borrowing on both Arbitrum and Avalanche, with the only funds protected being deposits in the ‘Depositor vaults’. Steadefi’s TVL fell from over $2M to just $550k.

 At least some of the remaining TVL appears to have been locked in contracts by the exploiter:

 However, the exploiter has also paused the farms contract, which means that if you (and the majority of everyone is) has your svTokens or ibTokens deposited in the farms, you will not be able to withdraw them as well. However, the exploiter is also unable to withdraw them.

 The funds were swapped to ~625 ETH and bridged to Ethereum before being forwarded onto another address , where they remain.

 Attacker’s address ( ETH , ARB , AVAX ): 0x9cf71F2ff126B9743319B60d2D873F0E508810dc 

 With many projects having funds returned recently, Steadefi may be hoping for a happy ending. 

 However, given that this incident was due to an account compromise and not a potential whitehat poking about for bugs in a smart contract, we won’t be holding our breath.

 Especially if certain state-sponsored phisherman are involved… 

 But who knows, between Arkham’s opening of a public doxx-market and Curve’s bounty hunter reward , we may be seeing the emergence of a new post-hack strategy.

 In the case of Curve, one bounty hunter (or on-chain bluffer) has already opted to go straight to the source rather than take the 10%:

 Hacker. I have your IP address. I give you until 08/10/23 8:00 AM UTC to return: 7,000,000 CRV and 7,000 WETH to this address: 0xC6a194f5F08352C6aD0B9Dcff1C7A5Ef9f8A7802. After this time I will reveal your IP address. This is your last chance to make the right choice.

 Blackmailing a blackhat. 

 Is there really no honour among thieves? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

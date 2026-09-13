# [H] Swaprum exploit: Swaprum, an Arbitrum-based DEX, pulled the rug for $3M on Thursday

## Summary
Severity: High
Target: Swaprum
Loss: $3,000,000
Published: 05/18/2023
Source: https://rekt.news/swaprum-rekt
Type: rekt-postmortem

## Details
## Swaprum - REKT

 Saturday, May 20, 2023 Swaprum - Arbitrum - Rugpull - REKT 

 read this article also in : 

 Swaprum, an Arbitrum-based DEX, pulled the rug for $3M on Thursday. 

 While the project’s social media presence and GitHub repos have been deleted, Swaprum’s website remains live, proudly displaying Certik’s seal of approval in its banner.

 This latest incident comes less than a month after Merlin DEX rugged $1.8M , sparking a debate as to whether a Certik audit was more of a red flag than a mark of confidence.

 This is the 4th rug over $1M we’ve covered so far this year, all of them supposedly audited.

 But not all audits are created equal…

 When will we learn? 

 Credit: Beosin 

 As with most rug-pulls, the mechanics behind the incident were not complicated. 

 The project’s reward contract was upgraded to a new version which included the backdoor function add() . 

 add() sends users LP tokens to the team’s Deployer address, which was able to steal the funds by draining the underlying liquidity.

 Attacker address (Swaprum: Deployer): 0xf2744e1fe488748e6a550677670265f664d96627 

 Example tx: 0x36fef881… 

 Funds were bridged to Ethereum where a total of 1620 ETH was deposited into Tornado Cash.

 It should be noted that the upgraded (malicious) contract was not included in the audit . But the capability to upgrade contracts containing user funds to an arbitrary deployment was always there...

 Certik does mention major centralisation issues in Swaprum’s code, remarking that the contract owner has authority over certain aspects of the protocol. 

 However, the wording mainly refers to external threats:

 Any compromise to the _owner account may allow the hacker to take advantage of this authority…

 If an attacker compromises the account, he can change the implementation of the contract and drain tokens from the contract.

 Given the recent backlash, one would think that auditors might make an effort to be more explicit about the potential for malicious insiders, reflecting the fact in the report’s wording. 

 A simple ‘ruggability’ score would go a long way to communicating these risks in a degen-friendly format.

 However, the idea probably wouldn’t go over well with grifters looking to rubber stamp their latest scam. 

 Certik has since updated Swaprum’s security score to “Exit Scam”. 

 Too little, too late? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

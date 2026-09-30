# [C] Badger exploit: $120 million taken in various forms of wBTC and ERC20

## Summary
Severity: Critical
Target: Badger
Loss: $120,000,000
Published: 12/02/2021
Source: https://rekt.news/badger-rekt
Type: rekt-postmortem

## Details
## Badger - REKT

 Thursday, December 2, 2021 Badger - REKT 

 read this article also in : zh 

 rekt roadkill. 

 The badger is dead. 

 $120 million taken in various forms of wBTC and ERC20.

 A front-end attack places Badger DAO at number four on the leaderboard . 

 rekt.news repeats: 

 Infinite approval means unlimited trust - something which we know we shouldn’t do in DeFi. 

 But should regular users be expected to spot an illegitimate contract via wallet approvals if the front-end is compromised? 

 An unknown party inserted additional approvals to send users' tokens to their own address. Starting from 00:00:23 UTC on 2.12.2021, the attacker used this stolen trust to fill their own wallet. 

 As the news of users’ addresses being drained reached Badger, the team announced they had paused the project’s smart contracts, and the malicious transactions began to fail around 2 hours 20 mins after they had begun.

 BadgerDAO’s aim is to bring Bitcoin to DeFi. The project is made up of various vaults for users to earn yield on wrapped BTC variants on Ethereum.

 The vast majority of stolen assets were vault deposit tokens which were then cashed out, with the underlying BTC bridged back to the Bitcoin network, and any ERC20 tokens remaining on Ethereum.

 The current locations of the stolen funds is summarised here . 

 Rumours that the project’s Cloudflare account was compromised have been circulating, as have other security vulnerabilities .

 The approvals presented themselves when users attempted to make legitimate deposit and reward claim transactions, building a base of unlimited wallet approvals that allowed the attacker to transfer BTC related tokens directly from the user’s address. 

 The first instance of approvals for the hacker’s address was almost two weeks ago, according to Peckshield . Anyone interacting with the platform since then, may have inadvertently approved the attacker to drain funds.

 Over 500 addresses have approved the Hacker’s address: 0x1fcdb04d0c5364fbd92c73ca8af9baa72c269107 

 Check your approvals and revoke here: etherscan.io/tokenapprovalchecker 

 Example transaction : draining ~900 byvWBTC, worth over $50M. The victim had approved the attacker’s address to spend unlimited funds via the increaseAllowance() function around 6 hours earlier.

 Eventually, thanks to an “ unusual ” feature in Badger’s transferFrom() function, the team was able to pause all activity, halting the further loss of funds. 

 If longstanding projects with such strong reputations as Badger can get rekt like this, and some of the biggest names in the game have their near-misses , DeFi users can’t afford to get too comfortable about the security of their biggest bags. Diversification is key to survival.

 Despite all the stress that’s usually placed on checking the URL and making sure you’re interacting with proper channels, this wouldn’t have helped users in this case.

 The front-end was manipulated at least 12 days ago . 

 How did Badger not notice? 

 A user flagged the suspicious increaseAllowance() approval in Discord. 

 Why did Badger devs not look into it? 

 For experienced users, these kinds of bogus approvals might be easy to spot, and checking the validity of any contract is easy enough by copy/pasting the address into Etherscan before signing the transaction.

 But for DeFi to reach “mass adoption”, these extra precautions must be streamlined.

 Until then, we can only practise good wallet and approval hygiene . 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

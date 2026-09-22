# [C] Vee Finance exploit: $34 million taken from Vee Finance earns them the number 7 spot on our leaderboard

## Summary
Severity: Critical
Target: Vee Finance
Loss: $34,000,000
Published: 09/21/2021
Source: https://rekt.news/veefinance-rekt
Type: rekt-postmortem

## Details
## Vee Finance - REKT

 Tuesday, September 21, 2021 Vee Finance - REKT 

 read this article also in : zh 

 Top ten thievery. 
 $34 million taken from Vee Finance earns them the number 7 spot on our leaderboard. 

 As AVAX rises in popularity, its crime rates increase accordingly. This is the second substantial loss on the Avalanche network this month.

 On the 12th of September Zabu Finance lost ~$3.2M; a small sum compared to today’s loss , yet still a huge haul for those who are not used to the drama of DeFi.

 What’s normal for us is not normal elsewhere. 

 34 million dollars stolen, but this story is just one of many. 

 The following is taken from the (first) official post-mortem. 
 Exploiter ETH Address: 0xeeee458c3a5eaafcfd68681d405fb55ef80595ba 

 Exploiter AVAX Address: 0xeeeE458C3a5eaAfcFd68681D405FB55Ef80595BA 

 The exploiter’s Ethereum address was funded via TornadoCash in three lots of 10 ETH: ONE , TWO , THREE .

 The funds were then bridged to Avalanche, where the attacker swapped 26.999006274904347875 WETH.e for 1,369.708 AVAX via Pangolin.

 The attacker then deployed exploit contract 1 and used it to firstly swap AVAX for the targeted tokens, then create the following trading pairs:

 QI/WETH.e 

 XAVA//WETH.e 

 LINK.e/WETH.e 

 QI/LINK.e 

 XAVA/LINK.e 

 XAVA/WBTC.e 

 LINK.e/WBTC.e 

 Once the attack contract had been funded with 20 AVAX in 5 addresses, the preparation was complete and the exploit execution could begin. 

 After initially failing due to low gas, the attacker was able to use a dynamic contract to conduct leveraged trading on the QI/WETH.e pair, before failing again.

 After deploying a new attack contract , the same steps were used, this time successfully.

 Repeated trades of USDT.e to ETH.e were made via AugustusSwapper.

 And a third attack was deployed. 

 During leveraged trading, Vee Finance uses a single source price oracle: the prices of assets in the Pangolin pools. Via trading between these newly created pairs, the attacker was able to manipulate the prices that Vee Finance referenced.

 This manipulation, together with the fact that price acquisition wasn’t processed for decimals, allowed for the approval of transactions that would usually not pass the protocol’s slippage check.

 For an in-depth analysis of the exploit, see Vee Finance’s second post-mortem of the day.

 The stolen funds were bridged back to Ethereum during and after the attack, over a series of over 100 transactions, for example this transaction. 

 The exploiter’s Ethereum wallet currently holds a total of 214 WBTC ($9.3 M) and 8,804 WETH ($26.9M) 

 According to Vee Finance’s incident report “The VEE team is actively working to further clarify the incident and will continue to try to contact the attacker to recover the assets” and are appealing to the hacker to take a bug bounty. 

 The team sent a transaction to the exploiter’s addresses on both Ethereum and Avalanche , with the following message, also sharing on Twitter :

 Hello, this is vee.finance team. We are willing to launch a bug bounty program for the bug you identified, please contact us via contact@vee.finance .

 Other incoming transactions contained messages, too, ranging from warnings: 

 Your address has been caught by the team

 To self-promo :

 Hello this is @yannickcrypto, please follow me on twitter https://twitter.com/yannickcrypto _

 To outright begging on-chain: 

 Big man, send me some for a poor man who can't afford to eat

 At press time, there was still no response from Big man. 

 Vee Finance ignored the recommendations given in their Slowmist audit , and their Certik audit wasn’t much help either. 

 Any project which appears in “pump groups” such as this one is not doing well at all.

 Will we see a vee-shaped recovery, or has all the value veritably vanished? 

 (Please consider the task of your anonymous author when naming your protocols) 

 If you enjoy our work, please donate to our Gitcoin Grant. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

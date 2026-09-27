# [C] Compounder Finance exploit: The rekt reaper has a way of making people talk

## Summary
Severity: Critical
Target: Compounder Finance
Loss: $12,000,000
Published: 12/02/2020
Source: https://rekt.news/deathbed-confessions-c3pr
Type: rekt-postmortem

## Details
## Compounder Finance - REKT

 Wednesday, December 2, 2020 c3pr - audit - rugpull 

 read this article also in : zh 

 The rekt reaper has a way of making people talk. 
 In the final moments, as TVL approaches zero, and the drawdown becomes unbearable, a faceless figure enters the chat.

 When a protocol is wounded beyond repair, and it’s time has come to shuffle off this mortal coil, the fourth and final horseman arrives to guide them to the afterlife, presenting himself in .gif format.

 Compounder.finance was rug pulled for over $12,000,000. 

 In our volatile community, greed and desperation are punished and rewarded in equal yet unpredictable ways.

 Here there is hope for the sinner, whose transgressions are forgotten as they escape down-chain in their cloak of anonymity.

 Rekt is here to shine a light on the sinful - to expose their methods so that we all can learn.

 The compounder.finance site and Twitter account were deleted instantly. 

 A completed security audit offered our detectives the only lead. 

 These are busy times at RektHQ , a few hours had already passed when we started to investigate… When we contacted the auditors for a quote, they were less than pleased to see us.

 Please don’t send death shit like that, you for real had me scared for my safety for a minute over here and weaker hands might report that or some shit. 

 After our detective offered some reassurance, Solidity.finance provided us with the full chat logs of their conversation with compounder.finance.
 
Other victims also reached out to us, showing early conversations with compounder admins where they voiced their concerns.
 
Solidity.finance told us that they had only briefly spoken with the admins, and although they had indeed audited the contract, they had stated in the document that although the pools were treasury controlled by a timelock, that the timelock offered no protection. 
 The following message is from their chat logs.
 
At this stage in our investigation, solidity.finance was still a suspect. We wanted to know why they had thought that the compounder.finance team seemed ”very trustworthy”
 
When reading the chat logs, we noticed that although the accounts had been deleted, one username remained - “keccak”.

Although solidity.finance said keccak had deleted their account, we had already found their account and were trying to make contact.
 
Unfortunately, Vlad didn’t want to talk on the phone, so we sent them a message, not expecting him to respond. 
 Until…
 
 Vlad was ready to talk. Unfortunately, he wasn’t very cooperative.
 
Vlad / keccak can still be reached on Telegram via @keccak, however he no longer responds, and has since deleted the images on his account.
We attach his old avatars here for your consideration and investigation. 
 We have been informed that - The wolf one is from a famous Ukrainian cartoon in Russian, which says “come by if something comes up” 

 The left one is a anti-nuclear-weapon poster. 

 Not much help for the affected users unfortunately.
 
 Once it became clear Vlad wouldn’t talk, we visited the official Compounder telegram group, where it became apparent that our reputation precedes us. 
 
As we scrolled through the content of the chat, we saw all the typical behaviours that are caused by a freshly pulled rug.
 
 Even large players are humbled by the power of a rug pull. This group leader lost $1,000,000 and has opened his own investigation group (686 members) in an attempt to have some revenge. 
 
The thread can be found here . 
 The Statistics 

 As part of our investigation, we introduced Solidity.finance to @vasa_develop from Stake Capital and asked them to work together to create a full post-mortem of the incident.

 The following data is taken from their report .

 Assets Rugged (8): 

- 8,077.540667 Wrapped Ether ($4,820,030.07)

- 1,300,610.936154161964594323 yearn: yCRV Vault ($1,521,714.80)

- 0.016390153857154838 Compound (COMP) ($1.79)

- 105,102,172.66293264 Compound USDT ($2,169,782.85)

- 97,944,481.39815207 Compound USD Coin ($2,096,403.68)

- 1,934.23347357 Compound Wrapped BTC ($744,396.89)

- 23.368131489683158482 Aave Interest bearing YFI ($628,650.174379401)

- 6,230,432.06773805 Compound Uniswap ($466,378.99)

 Wallets with the funds after rug-pull 

 0x944f214a343025593d8d9fd2b2a6d43886fb2474 

- 1,800,000 DAI

 0x079667f4f7a0b440ad35ebd780efd216751f0758 

- 5,066,124.665456504419940414 DAI

- 39.05381415 WBTC

- 4.38347845834390477 CP3R

- 0.004842656997849285 COMP

- 0.000007146621650034 UNI-V2

- 

 From the time the Deployer was first funded via Tornado.cash to the time of the rug pull, the Deployer sent ETH to 7 different addresses. Most of these were one-off payments. One of these addresses , however, received 4 separate payments on Nov 19th, 20th, 22nd, and 23rd. Much of the funds from that address ended up an another address holding over 1 million KORE (Only 10k KORE existed before they rug pulled).

 The main culprit(s) of this hack were the 7 malicious Strategy contracts that were added to the codebase after the audit.

 A non-malicious withdraw() function from a Strategy contract looks something like this.

 Notice that we have some checks like:

These checks were missing in the 7 malicious Strategy contracts. This allows the Controller contract (which was controlled by the rug-puller strategist ) to withdraw the assets from the Strategy. 
 (Note the missing checks below in the malicious withdraw function)

The complete rug-pull can be explained in 4 steps. 
 Step 1 

 Compounder.Finance: Deployer deployed 7 Malicious Strategies with manipulated withdraw() functions.

 Step 2 

 Compounder.Finance: Deployer Set and Approve 7 Malicious Strategies in StrategyController via Timelock (24h) transactions.

 Step 3 

 Compounder.Finance: Deployer (strategist) called inCaseStrategyTokenGetStuck() on StrategyController which abuse the manipulated withdraw() function of the Malicious Strategies to transfer the tokens in the Strategies to the StrategyController. Do this for all 7 Malicious Strategies.

 Step 4 

 Compounder.Finance: Deployer (strategist) called inCaseTokensGetStuck() on the StrategyController which transfers the tokens from the StrategyController to the Compounder.Finance: Deployer (strategist) address. Now the Compounder.Finance: Deployer (strategist) has full control over 8 assets valued at $12,464,316.329.

 From here the assets have been transferred to multiple addresses listed here .

 Excellent work from @vasa_develop . 

 If you are a whistleblower, cyber sleuth or Etherscan detective and you have something to contribute, contact us. 

 Judgement Day: 
 Who is to blame?

 After our analysis, we know it’s not the auditors, who dutifully completed their task, making sure that Compounder Finance stayed safe from external attacks, while also voicing their concerns in their audit report and the TG chat .

 Perhaps they could have voiced these concerns slightly louder, but in the end, the ultimate responsibility will always lie with the depositor.

 Compounder.finance used a timelock as an indicator that they wouldn’t pull the rug. We know now that this method can’t be trusted. If it is used, an automated alert system or dashboard should be put in place to monitor transactions at that address.

 24 hours appears to be insufficient to provide enough warning for users to remove funds.

 Not all projects with anonymous founders are scams. This entire industry was founded by an anon. 

 However, nearly all scams are projects with anonymous founders. As a community, we need to be wary of these projects; especially those who use untraceable sources of funds like Tornado.cash.

 The mere existence of an audit report is not sufficient to assure a projects' safety or legitimacy. Audits often focus on risks from external attackers more than internal - perhaps this is an area where auditors need to improve.

 Even with audits, timelocks and burnt keys, depositors are always at the mercy of other users, who may dump huge amounts of tokens onto the market at any time.
 
 Solidity.Finance: The Official Statement 
 
 The Compounder team swapped the safe/audited Strategy contracts and replaced them with malicious 'Evil Strategy' contracts that allowed them to steal users funds. They did this through a public, though clearly unmonitored, 24-hour timelock. 

 This issue of centralized control by the C3PR team was raised in our audit report and our discussions with their team. The team had the power to update strategy pools and they did so maliciously here to steal users’ funds. In an effort to be transparent, anyone can view our chat logs with the C3PR team here: 

 Historically, our audits have focused on the risks to projects from external attackers, with some discussion on risks posed by project teams as we did here. We will take this unfortunate event as a learning opportunity, and moving forward will provide more robust details in easy to understand language on risks stemming from developers’ control. 

 We all know we should read smart contracts before we invest, but the knowledge barrier is high. Not everyone knows what to look for, and those who do are not incentivised to share their findings.

 In the case of C3PR, users who listened were made aware of the danger very early on, and the code that made the rugpull possible was always present.

 Despite this, over $12,000,000 accumulated in the contract, which can now be labelled as one of the largest rug pulls of all time.
 
## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

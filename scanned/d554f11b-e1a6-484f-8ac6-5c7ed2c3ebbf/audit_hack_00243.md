# [C] Sonne Finance exploit: The alarm has been rung on Sonne Finance, as a $20 million flash loan attack reverberates across the crypto sphere, chiming a somber melody that warns

## Summary
Severity: Critical
Target: Sonne Finance
Loss: $20,000,000
Published: 05/15/2024
Source: https://rekt.news/sonne-finance-rekt
Type: rekt-postmortem

## Details
## Sonne Finance - Rekt

 Thursday, May 16, 2024 Sonne Finance - REKT 

 read this article also in : zh 

 The alarm has been rung on Sonne Finance, as a $20 million flash loan attack reverberates across the crypto sphere, chiming a somber melody that warns of the perils lurking in the DeFi shadows. 

 Nerv Alert sounded the alarm on late Tuesday, initially detecting a $3 million loss.

 Sonne made an announcement on Discord soon after the attack. But did not announce it on X until a couple of hours after. 

 Soon after the loss tallied up to $20 million in WETH, VELO, soVELO and Wrapped USDC.

 The Optimism chain of Sonne Finance was exploited through a known donation attack on Compound v2 forks. 

 Another fork of Compound v2, Hundred Finance was rocked by a similar exploit roughly a year ago.

 Hundred Finance sent out a warning to other Compound forks after their attack.

 It appears that Sonne seemingly turned a deaf ear, because this was an attack that could have been prevented. 

 Will these protocols ever learn? 

 Credit: Nerv Alert , Luke Youngblood , Daniel Von Fange , Tony KΞ 

 Rinse, repeat, rekt - another DeFi protocol gets taken to the cleaners by a known exploit. 

 A fork of Compound V2, Sonne held just over $60 million in TVL prior to the exploit.

 In an infuriating display of ignoring history, Sonne became the latest Compound fork to succumb to an exploit that had already taken down protocols like Hundred Finance a year prior.

 Luke Youngblood provided an attack breakdown : 

 The Sonne Finance team deployed a new market contract for $VELO and a governance proposal was created to activate the market, which had a 4 day total governance period before going live.

 When the governance proposal succeeded 3 days later, and the 24 hour timelock expired, it was now executable by anyone on the Optimism network. The attacker made sure they were the one to execute it, probably by running a bot and hoping they were first to strike.

 The attacker executed the proposal, along with their attack payload, all in a single transaction. The proposal set the collateral factor on the Sonne $VELO market to 35%, which enabled the attack to occur, and the protocol to immediately be drained of at least 7 figures of funds.

 Attacker: 
 0xae4a7cde7c99fb98b0d5fa414aa40f0300531f43 

 Attack Contract: 

 0x02fa2625825917e9b1f8346a465de1bbc150c5b9 

 Target Contracts: 

 soVELO: 0xe3b81318b1b6776f0877c3770afddff97b9f5fe5 

 SoUSDC: 0xec8fea79026ffed168ccf5c627c7f486d77b765f 

 soWETH: 0xf7b5965f5c117eb1b5450187c9dcfccc3c317e8e 

 Attack Transaction: 0x9312ae377d7ebdf3c7c3a86f80514878deb5df51aad38b6191d55db53e42b7f0 

 Stolen Funds currently held in several addresses: 

 0x5d0d99e9886581ff8fcb01f35804317f5ed80bbb 

 0x6277ab36a67cfb5535b02ee95c835a5eec554c07 

 0xae4a7cde7c99fb98b0d5fa414aa40f0300531f43 

 0x9f09ec563222fe52712dc413d0b7b66cb5c7c795

 0x3b39652151102d19ca41544a635956ef97416598 

 0x9f44c4ec0b34c2dde2268ed3acbf3aba8eacde51 

 Daniel Von Fange delved deeper into the critical errors committed by Sonne, and provided recommendations for protocols employing multisig wallets alongside timelock governance. 

 The TL;DR: if a series of actions must happen in a certain order in order to be safe, make sure your governance process doesn't allow picking and choosing what to execute, be atomic.

 Sonne was quick to issue a Post-mortem on the exploit roughly 5 hours after the attack. 

 They highlighted how they previously avoided the Compound V2 donation attack by slowly increasing collateral factors, but a recent proposal to add VELO markets opened an exploit window. 

 After scheduling VELO integration transactions through their permissionless Optimism multisig, the attacker executed the changes and drained $20M by leveraging the well-known vulnerability.

 Sonne Finance is working to recover the stolen funds, considering a bug bounty for their return.

 But it wasn’t all bad news. MEV researcher Tony KΞ from fuzzland posted a play by play of how they prevented more than $6.5M from being hacked during the incident, using just $100. 

 One user noticed something fishy when they posted that Mendi Finance's code is a friendly fork of Sonne Finance .

 Could they be exploited soon?

 Sonne was audited by Yearn Finance's yAudit. 

 The attack vector is listed as high finding, stating “Unclear protection against Hundred Finance attack vector.” 

 This latest attack on a Compound v2 fork has speculation floating around that other forked protocols could be exploited

 This is a known vulnerability that can be easily prevented, hopefully this latest incident will put this on other forked protocol’s radars. 

 Do you think they will do their due diligence or will we see more similar attacks? 

 The $20 million attack on Sonne Finance represents a major breach enabled by failure to properly address a well-known vulnerability. 

 Despite explicit warnings from previous incidents like the Hundred Finance exploit, Sonne's team pushed ahead with integrating new markets without comprehensive safeguards against the donation attack vector. 

 This oversight, coupled with loosely configured governance permissions, allowed the attacker to drain millions with relative ease.

 The fact that auditors had explicitly flagged this risk as high-severity makes this incident even more inexcusable and concerning. 

 As speculation swirls around other Compound V2 forks potentially being exposed to the same exploit, the incident serves as a wakeup call.

 Prioritizing swift deployments over comprehensive security reviews is a trade-off no protocol can afford, as Sonne has learned the hard way. 

 For DeFi to reach maturity, teams must move past blindly copying code they don't fully understand.

 Rigorous pre-launch audits, real-time monitoring for attack vectors, and recovery mechanisms are essential. Otherwise, the ecosystem will remain trapped in a cycle of relearning the same costly lessons with each keystroke. 

 The burning question is whether Sonne's $20 million lesson will be the final straw that forces positive change or will the acceptable loss figures simply keep increasing until major investors and users lose faith altogether? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

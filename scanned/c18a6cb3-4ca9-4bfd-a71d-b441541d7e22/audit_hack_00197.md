# [C] Pickle Finance exploit: The Pickle Finance cDAI jar was hacked for 19.7 million DAI via a vulnerability involving fake “Pickle Jars”

## Summary
Severity: Critical
Target: Pickle Finance
Loss: $19,700,000
Published: 11/22/2020
Source: https://rekt.news/pickle-finance-rekt
Type: rekt-postmortem

## Details
## Pickle Finance - REKT

 Sunday, November 22, 2020 pickle finance - Rekt 

 read this article also in : zh 

 The fermentation of finance continues. Even pickles have a shelf life. 
 The Pickle Finance cDAI jar was hacked for 19.7 million DAI via a vulnerability involving fake “Pickle Jars”.

 Pickle Finance has become the latest victim of the hack epidemic. 

 However, this time, something is different... 

 As Twitter tried to come to terms with yet another financial fatality, Rekt started to investigate.

 We contacted the Stake Capital team, who looked at the code and warned us that other jars could be at risk.

 We then quickly contacted the Pickle Finance team and set up a war room between members of Stake Capital (@ bneiluj , @vasa_develop ) Yearn ( @bantg ) Pickle Finance and experienced developers @ samczsun , @emilianobonassi .

 As we worked, it became clear we were looking at something very different to the recent DeFi lego style hacks of recent weeks.

 This was not an arb. 

 The attacker had excellent knowledge of Solidity and EVM, and had likely been paying close attention to the Yearn code for some time, as the vulnerability was similar to one which was discovered in the Yearn code a month earlier.

 Pickle Jars are essentially a fork of Yearn’s yVaults. These Jars are controlled by a contract called the Controller, which has a function that allows users to swap their assets between Jars.

 Unfortunately, there is no whitelist for which Jars are allowed to use this swapping function.

 The hacker had created a fake Pickle Jar and swapped the funds from the original jar. This was possible because the swapExactJarForJar didn’t check for "whitelisted" jars.

 The Pickle Finance team knew they needed help, and were more than willing to work with the others to prevent any further damage.

 Pickle had tried to call “withdrawAll”, but the transaction failed .

 The withdrawal request had to pass through the Governance DAO which had a 12 hour timelock.

 Only one member of the Pickle multisig had the ability to bypass the timelock, and they were asleep.

 This meant admins couldn’t empty the Pickle Jars, but it didn’t protect them from another hack.

 Pickle Finance and Curve sent out warnings telling users to withdraw their funds from Pickle immediately, however, $50 million remained in the potentially vulnerable pickle jars, while the white hat team investigated the exploit and checked the safety of remaining funds.

 The rescue team either had to wake the sleeping admin, or drain the jars themselves.

 The team had to overcome five major challenges. 
 
- 
 To get the Pickle Finance team together across several time zones to start rescuing the funds by pushing transactions into 12h timelock (via 3 out of 6 multisig) to withdraw funds.

- 
 To get thousands of investors to withdraw their funds (and discourage them from redepositing once the pool TVL dropped and the APY inflated to 1000+% APY)

- 
 Performing safety checks on the other jars to see if there is a possibility of more attacks.

- 
 Duplicating the attack and whitehacking before anyone can hack the jars again.

- 
 Avoiding getting front-runned when trying to rescue the remaining 50k

 How long can we continue to rely on pseudo anonymous white hat hackers for help? 

 The incentives are clearly more aligned for attackers than protectors; why would they co-ordinate such a gruelling counter attack?

 The glory goes to whitehacks, yet the money goes to hackers. That’s not sustainable. 

 How long until the temptation turns these white hats black?

 Analysis 

 By releasing this technical information we are aware that we could be triggering new hacks. We discussed the potential consequences with Pickle Finance and other developers, and confirmed that we do not know of any operational forks of Pickle that could be affected by copycat attacks.

 Selective disclosure would introduce an aspect of liability, so we decided to release this information freely. If any protocols are running a fork of Pickle’s code, they should already be aware of the unfolding events and be taking preventative action against copycat hacks.

 The following chart was created by @vasa_develop .
 
The original file can be found here . 
 For further details see the teams full post-mortem here. 

 It will be interesting to see how the relatively new insurance primitive “ Cover Protocol ” handles this incident; a large amount for their first claim. The snapshot vote for the insurance claim can be found here. 
 
 Pickling is a slow process. 
 For decades, agile development evangelists have told developers to move fast, fail quickly and release the minimum viable product.
These ideas don’t fit the bill when building in a hostile environment.

 Failing quickly in DeFi comes at great expense. 

 We don’t simply need another methodology. We need a paradigm shift allowing for rapid iteration while reducing the likelihood of getting rekt at the same time.

 Let’s eliminate the idea that an audit is a guarantee for safety. It is – most of the time – a snapshot of checklist-style security measures applied to moving targets that have often evolved into something else shortly after a project hits mainnet.

 The audits from MixBytes (October 3rd) and Haechi (October 20th) were completed before the addition of ControllerV4 (October 23rd), which was one of the key attack vectors.

 The greatest teams in the future of finance will be those capable of handling the trade-offs between shipping fast and shipping safely , continuously auditing and rigorously testing their composable money robots on a regular basis.

 Audits should be a regular and continuous process, not a box to be ticked before launch. New DeFi protocols are subject to constant change and adaptation, and safety audits should reflect this.

 Pickles only stay fresh when they’re inside the jar... 
 photo @ martinkrung 
 EDIT - 18th July 2021. 

 Haechi reached out to us with the following statement:

 We audited a part of Pickle’s contracts, but the exploit occurred in newly updated smart contracts. The smart contract with the exploit was “swapExactJarForJar” in “controller-v4.sol”, and our scope of the audit was “controller-v3.sol” without “swapExactJarForJar”.You can find the details here. 
(FYI) I checked that your team mentioned that our audit for pickle finance was completed before the addition of ControllerV4 which was the key attack vector for this hack.

 You can find the details here. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

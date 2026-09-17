# [C] Unizen exploit: March 8th, $2.1M was stolen in multiple attacks on the ETH-based DEX shortly after a contract upgrade to their DEX aggregation contract

## Summary
Severity: Critical
Target: Unizen
Loss: $21,000,000
Published: 03/08/2024
Source: https://rekt.news/unizen-rekt
Type: rekt-postmortem

## Details
## Unizen - Rekt

 Tuesday, March 12, 2024 Unizen - REKT 

 read this article also in : 

 Not such a zen weekend for Unizen 

 March 8th, $2.1M was stolen in multiple attacks on the ETH-based DEX shortly after a contract upgrade to their DEX aggregation contract. 

 Cyvers sounded the alarm during the March 8th attack. Unizen acknowledged the hack 7 hours later.

 The attacks happened over a period of a few hours, leaving some users in the dark, believing the DEX was down due to the upgrade, not finding out until after the fact. 

 RevokeCash urged users to check whether their address was affected and revoke approvals via their dedicated tool .

 Upgradeable contracts are a common red flag for attacks. Highlighted recently by attacks on Socket , last year’s Safemoon and Level Finance to name a few. 

 Did another protocol rush to upgrade a contract without due diligence, setting themselves up for an exploit? 

 Credit: Cyvers , SunWeb3Sec , Martin Granstrom , Blocksec , Chain Aegis , Blockfence 

 Multiple attackers took advantage of an unverified external call vulnerability shortly after a DEX Aggregation contract upgrade upgrade on Unizen. 

 The upgrade was meant to reduce the cost of ETH gas fees, except something else was reduced.

 Users that had interacted with and approved a higher spending limit for certain tokens, were taken advantage of by a malicious actor that stole user funds. Resulting in a robbery worth more than $2.1M. 

 Attacker 1: 0xb660cae1a59336676ea1887b15eb3c0badb90d78 

 Attack Contract 1: 0xb660cae1a59336676ea1887b15eb3c0badb90d78 

 Attack Transaction: 0xc12a4155c2c90707138e4aef8883c8f724371145823e2f661f19b93e5b3a9d6e 

 Attacker 2: 0xc596523b77ceb9567279B572c653ECF4BA763CB7 

 Attack Contract 2: 0x90a7482dD7fA28865f440EC0c3B783775AC01266 

 A total of 14 attack transactions were carried out.

 Attack Address 3: 0xd440b92739f86b00d1135b5eea871751433da2d7 

 Attacked Contract 3: 0x2f744f784000de0b8f1a7da3f0021ad56c09ce1a 

 Attack Transaction: 0x30fef86a72ea7e1109ffeae572439995c78561ffeb968dcbd61c609efc60fdd9 

 Attacker 4: 0x4e2ce48f0b5d97bfd4be3f6c7b6479db1aa5b365 

 A total of 13 attack transactions were carried out.

 The flow of funds can be found here .

 Stolen funds were sent to this address .

 Not helping matters, the X feed filled with phishing spam posts tagging Unizen, burying the news of the hack. Unizen caught the spam situation shortly after.

 Unizen addressed the community 7 hours after the attack, offering to address concerns and start the healing process for their community. 

 The protocol’s CTO went into further detail , highlighting the gas optimization upgrade was a minor bug with great consequences.

 2 days after the hack, Unizen sent several onchain messages addressing a “Security Professional”, offering a 20% bounty to return the funds. 

 On-chain Messages:

 0x13f8220624f61cfb002489821eeba9df392150285147c1aaf816f283ae7cc43e 

 0x351906b2406282042c7396ea960b7a52d305658097e3f25bae79be4cdbb7c311 

 0x015b7fd22c027abb9c237a4ecb3862b7c3f2acb857fe93175e4a6c8265d38857 

 0x0dc8ce3e98d006cd1ba446544b289d960477347e8826efa788d6b879a59cd09d 

 0xcbdba5e11d3becfe80f8fd710d04fd068ad722289869459a7ce4f1e7123e5946 

 0xdcfed8e883eec7f913c452b2ed0da29f3504722479400053482cddd7797f883f 

 0xd5d684f3f61de25bd04b8434bb9af23658377350dee16ed2575d377426cebd89 

 A few hours later, Unizen announced they will reimburse losses below $750,000 with USDC or USDT. CEO and Founder, Sean Noga loaned the protocol with his personal funds. 

 They even posted a video in the same announcement on how to revoke spend limit approvals on the Unizen platform. Where was this the day of the attack?

 Later in the day, the CTO announced that they have enough evidence to proceed with the post-mortem.

 Adding that an upgrade was patched to the gas optimization contract. Claiming they will invest a lot more in ensuring the security with every upgrade introduced, no matter the risk assessments and internal reviews. 

 But one of the crooks may not be finished.

 Caught by Blockfence on March 11th, one of the attackers may have moved on to their next onchain sleight of hand. 

 They deposited 128 ETH of stolen loot in an LP on Uniswap , with the Yoink token.

 They even left a message stating all profits from highly profitable trading strategies will be reinvested into Yoink. Did you mean to say hacking strategies? 

 Halborn and Verichain audited Unizen's DEX Aggregator in 2022, no documentation can be found for an audit on the recent upgrade.

 Do you think this attack could have been prevented with an audit to their recent upgrade? 

 Another external call vulnerability and another attack on an upgradeable contract, when will this madness end? 

 A costly mistake that could have been prevented with thorough testing and auditing. 

 Blackhats have to be foaming at the mouth with a checklist of upcoming contract upgrades just waiting to pounce and run away with the loot.

 The team's response may have been slow to keep their community updated, but it was refreshing how they handled the situation a few days later. 

 Users have already started to pour in to Unizen's Telegram and on X, thanking them for starting the reimbursement process, it appears they are following through so far.

 Not every hacked protocol reimburses users who get robbed. If the hack was a bigger hit, do you think they still would?

 Ensuring the security with every upgrade will surely be watched by blackhats waiting to pounce. 

 Will Unizen continue to follow through and live up to their name? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

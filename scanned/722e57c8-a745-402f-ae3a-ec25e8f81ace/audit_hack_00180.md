# [H] New Market Trading exploit: $3.98 million drained from 88 Gnosis Safes across Ethereum, Base, and Arbitrum in under two hours, Not by breaking Squid, not by breaking Safe, but by

## Summary
Severity: High
Target: New Market Trading
Loss: $3,980,000
Published: 5/25/2026
Source: https://rekt.news/newmarkettrading-rekt
Type: rekt-postmortem

## Details
## New Market Trading - Rekt

 Thursday, May 28, 2026 New Market Trading - Access Control Failure - Rekt 

 read this article also in : 

 Everyone called it the Squid hack . It wasn't. 

 $3.98 million drained from 88 Gnosis Safes across Ethereum, Base, and Arbitrum in under two hours, Not by breaking Squid, not by breaking Safe, but by exploiting a module nobody audited, built by a company most people had never heard of, running on a permission nobody revoked. 

 New Market Trading promised clients a "next-era solution for onchain wealth." Non-custodial. Secure. Human-supported. Their About page pledges to "push boundaries, respect risks" and to never "shy away from telling you where the dangers lie."

 Their module accepted a caller-supplied constant string as proof that a message was secure . Anyone who read the source code could pass it.

 Blockaid caught it live .

 The attacker could have been watching the permission contracts for three months , waiting for enough value to make the move worth it.

 By the time the real builder's name emerged, the funds were already DAI, sitting untouched in a single consolidation wallet while NMT reached for the attacker's attention via on-chain message. 

 When a platform built around the promise of security ships a module with a master password printed in the source code, what exactly were clients paying for? 

 Credit: The Block , Common Prefix , QuillAudits , w3cmx , New Market Trading , squid , Blockaid , PeckShield , bein crypto , Huntor , Fig , Rahul Rumalla , Defimon , Frank Hepworth 
 In the early hours of May 25th, while most of the security world was asleep, Blockaid wasn't. 

 The firm posted live as the attack unfolded - 88 Gnosis Safes being drained across Ethereum, Base, and Arbitrum simultaneously , all stolen tokens routing through attacker-controlled Uniswap V3 pools into DAI. Exploiter address named. Consolidation wallet flagged. Example transaction on-chain .

 The damage estimate at first alert : ~$3M in roughly two hours.

 PeckShield followed shortly after with a key detail Blockaid hadn't yet published , the attacker's starting capital.

 2.1 ETH from Tornado Cash , seed money for a $3.98 million operation . 

 The exploiter's wallet already held the proceeds . 

 By this point, the name on the contract had done its damage.

 The vulnerable contract was verified on Basescan under the name "SquidRouterModule." That was enough.

 Crypto news outlets ran with it . Headlines called it a Squid Router exploit. Twitter threads piled on as well .

 Coverage framed it as an attack on the cross-chain routing protocol - a protocol that had nothing to do with it, had never seen the code, and had never spoken to whoever built it. 

 The block explorer verification badge, the name in the source, the Squid integration in the module's logic, all of it pointed readers toward the wrong builder. 

 Verification on a block explorer means one thing: The source code is publicly readable. It is not an endorsement. It is not an audit. It does not establish who built the contract or whether it is safe.

 In this case, it handed the attacker a caller-supplied constant string to copy and handed the press a name to misattribute .

 Then came the plot twist the headlines ran with.

 Squid posted a clarification that landed like a corporate hostage statement - measured, urgent, and very careful with every word : "This incident is unrelated to Squid's core protocol and contracts. All Squid users and integrators are unaffected and no action is needed."

 They weren't done: "The vulnerable contract is verified on Basescan under the name 'SquidRouterModule' but this contract was not built, deployed, or operated by Squid. It is a third-party smart-wallet product that chose to integrate with Squid, among other protocols, but has not been in contact with us." 

 The closer stung : "The contract shares our name but is not our code."

 Squid co-founder Fig was blunter on Twitter : "The contract called SquidRouterModule is unrelated to Squid. We don't know yet who wrote or deployed this."

 They did know by the end of day. Everyone did.

 Safe Labs CEO Rahul Rumalla followed with a four-part thread of his own - same energy, different angle. The core contracts were fine. Only Safes that had manually enabled this specific third-party module were hit. The accounts affected didn't appear to have been created through Safe's official products at all. 

 He pointed users to Safe Shield , the firm's own risk detection tool, built to surface warnings for unverified or risky modules such as this one. 

 The name everyone wanted took longest to emerge. QuillAudits attributed $3.78M in losses to New Market Trading , the highest figure of any source, a gap explained by two tokens with no available price feeds at the time of initial on-chain accounting.

 Defimon's automated alert filled the identity gap the early reporting left open , naming NMT and CEO Frank Hepworth as the builder behind the contract.

 Common Prefix, who noticed the incident while it was unfolding, was more cautious: "At the time of writing, the identity of the module deployer has not yet been confirmed, but given a recent Blockscan Chat message it's possible that NewMarketTrading is behind the SquidRouterModule."

 By the time the real builder was publicly identified, the attacker had been sitting on 3.07M DAI for hours. 

 When security firms name the victim, the attacker, and the root cause before the team behind the contract does, who was actually watching this infrastructure? 

## The Password Was in the Source Code

 NMT built their platform around a simple premise : User funds live in individual Gnosis Safes, and an off-chain delegate bot handles the execution - swaps, approvals, yield strategies - on each user's behalf. 

 To bridge that off-chain delegate logic to on-chain Safe actions, NMT built the SquidRouterModule on top of Axelar's cross-chain messaging infrastructure . 

 That design choice is where everything went wrong.

 Axelar's expressExecuteWithToken() function skips gateway validation by design, meant for relayers pre-executing real cross-chain messages. 

 The observed attacks used Axelar Express Execution, that was how the calls reached the affected module, not the root cause .

 NMT reached for it as the entry point for privileged Safe actions, placed no additional access control behind it, and shipped it to production. 

 Two checks guarded the execution path . Neither held. 

 The first: sourceAddress == squidRouter, a caller-supplied string. Anyone can pass it. No signature. No cryptographic proof. No on-chain identity verification of any kind. Just a password, printed on the lock.

 The second check looked more meaningful. hasPermission(safe, delegate, APPROVE/SWAP) , a permission lookup against NMT's own PermissionsManager contract. Real delegates were registered there. Real permissions were recorded. The check ran against them.

 The problem: the delegate address being checked came from the caller's own payload, not from msg.sender.

 The attacker didn't need to be a real delegate, they just needed to know who one was. 

 Reading the PermissionsManager on-chain gave them the real delegate per Safe. Encoding that address into the payload and calling the function was all it took. 

 The permission check validated a real delegate's credentials, confirmed everything was in order, and never once asked who was actually calling.

 The missing line that stops all of it : require(msg.sender == delegate)

 One missing check made every user Safe drainable by anyone.

 308 successful drain transactions, 88 distinct victim Safes, across three chains. 

 The attacker deployed Foundry-based exploit contracts that called the module's DelegateBundler path to impersonate authorized delegates on victim Safes. 

 Each payload carried the real delegate address, an APPROVE action, PERMIT2 authorization, and a SWAP instruction.

 The module executed all three on the victim Safe in sequence - approving tokens, authorizing Permit2, then forcing a full-balance swap into an attacker-owned Uniswap V3 pool.

 Each Safe's entire balance routed into a worthless token called "u" , with a max supply of 42 holders, while the attacker, as sole LP, held the other side of every pool. 

 amountOutMin = 0 on every swap. No slippage protection required when you control the pool. 

 The attack ran across three chains . 

 Base started first , 06:11:37 UTC, 17 transactions in the opening minute.

 Ethereum followed 34 seconds later , 13 transactions in a single block.

 Arbitrum was hit simultaneously, adding 51 successful drain transactions before the operation ended.

 The drain phase was done in under 15 minutes . 

 229 Safes were exposed but never touched, either because the attack was detected and stopped by Blockaid, or because the attacker ran out of time.

 The permissions enabling all of this had been live since late February. Base granted from February 24. Ethereum from February 26. Nearly three months of open exposure. The attacker could have been monitoring the PermissionsManager contracts for months, waiting for enough value to accumulate.

 If the attacker was watching those contracts and waiting for value to accumulate, they had a patient three months to do it . 

 Axelar's express function was built for bridge relayers. NMT used it as a vault door. Did anyone ask whether those were the same thing? 

## Built Before the First Drain

 The attacker didn't improvise the exit. They built it weeks in advance. 

 The operation ran on five distinct wallets with separate roles. 

 Main operator - deployed attacker contracts, executed most calls, handled cross-chain consolidation via Relay, deployed the fake "u" token: 0x7c82cb4b2909c50c7c0f2b696eee7565e0a23bb8 

 Co-operator - received two 1 ETH Tornado Cash withdrawals, funded the main wallet with operational gas across all three chains: 
 0x9bdc730183821b6bb2b51be30b77c964fa645b91 

 Third wallet - made direct calls to the module, deployed 19 fake token contracts across Ethereum, Base, and Arbitrum: 
 0x7e54c729148a95bca651f3214ac9ebefd3fb1271 

 Fourth wallet - used separate fake tokens ("sasx", "sas", "ddxx v3"), funded via Orbiter Finance Bridge: 
 0xc8ef4003d9db3863b9af26afcf2275378bfa83e4 

 Holding wallet - received the consolidated DAI: 0xa447f71782135ab96a71374271a749ff7aa54859 

 Before a single Safe was touched, the main operator wallet deployed 19 Uniswap V3 liquidity pools , one for each token type held across the target Safes. 

 Every pool paired a real asset against the same worthless attacker-created token: "u." 

 Fake token "u": 
 0xe6Ff0FE017D09D690493deC0F0f55E8f9Cdc3512 

 The pool infrastructure was the weapon. The module vulnerability was just the trigger.

 When each drain was executed, the victim Safe didn't send tokens to the attacker. It was forced to swap its entire balance through the relevant attacker-owned pool - real assets in, worthless "u" tokens out. 

 amountOutMin = 0 on every swap. Victims received junk. The attacker held the other side of every trade. 

 Once the drain phase completed, the operator wallet removed liquidity from all 19 pools, collected the real assets, and used Relay to consolidate proceeds cross-chain before sweeping everything to the holding wallet. Clean.

 No direct transfer trail between victim and attacker. The protocol's own swap logic did the moving.

 Key attacker contracts as follows… 

 Ethereum: 
 0xfac7459683cdb9b6f367b42eedfebd745dc8760c 

 Ethereum: 
 0xe1d5fcfbba4d46f4937de369de415dd7e2d3265a 

 Base: 
 0x2d450322e3526f489afcc8c49923b35d355c70bc 

 Arbitrum: 
 0x2d450322e3526f489afcc8c49923b35d355c70bc 

 Arbitrum: 
 0x35b94f725bfdc1d00ef15df99dafadf6ecf3a0e9 

 Vulnerable Safe Module: 
 0x1f1d37a3Bf840e35c6a860c7C2dA71Fe555123ca 

 Sample Attack Transaction : 0x59d17fd31e31959b2d562508bf91c4fc1271682ba7d61a6209865e1151b69aea 

 The full haul across all three chains: 

 ~1.18M USDC ($1.18M) · ~12.44 cbBTC ($961K) · ~181 WETH ($383K) · ~371K apyUSD ($371K) · ~257K gtUSDCp ($257K) · ~97K cbXRP ($132K) · ~111K sUSDat ($111K) · ~107K steakUSDC ($107K) · ~1.243 WBTC ($95K) · ~286 wTAO ($82K) · ~25.2 steakETH ($55K) · ~45K SYRUP ($52K) · ~19.3 wstETH ($50K) · ~375K BNKR ($37K) · ~14.5k sparkUSDC ($14.5K)· ~151 AAVE ($13K) · ~9.5K LIT ($12K) · ~23K ONDO ($9.8K) · ~2.6K UNI ($8.7K) · ~25K CFG ($7.7K) · ~3K MORPHO ($7.2K) · ~56K ENA ($5.7K) · ~1.4K FLUID ($4.2K) · 3.5K USDT ($3.5K) · plus EUL, LBTC, ZRO, LINK, WLD, and others ( $12K) 

 Common Prefix's post-incident analysis put the total at approximately $3.98M across 308 successful drain transactions and 88 distinct victim Safes. Base was the largest loss surface, accounting for roughly 71% of total losses. Ethereum accounted for roughly 27%. Arbitrum roughly 2%.

 Everything was converted to DAI and swept into a single consolidation wallet .

 Consolidation wallet: 
 0xa447f71782135ab96a71374271a749ff7aa54859 

 DAI held as of publication: $3,070,767 in DAI

 The funds have not moved.

 The attacker's EOAs show near-zero ETH balances - consolidation was fast, conversion was clean, and the trail ends at a single address sitting visibly on-chain. No bridge hops. No mixing. No further movement. Patience, or confidence?

 229 Safes were exposed and never drained ,either because Blockaid's detection ended the run early, or because the attacker simply ran out of time. 

 On Ethereum, 151 Safes had active permissions. 24 were hit. 

 On Base, 148 were expose. 46 were drained.

 The math on what was left untouched is uncomfortable : The total potential exposure was substantially higher than what was taken.

 The Dune dashboard "Squid Router Exploit: The Drain Chain" tracked measurable USD losses across Ethereum and Base, with apyUSD and cbXRP excluded due to missing price feeds.

 The full picture, once Arbitrum and unpriced tokens are accounted for, lands at Common Prefix's confirmed 88 victim Safes. 

 When $3.07 million in DAI sits unmoved in a public wallet and the attacker hasn't responded to two separate contact attempts, are they waiting, or just not worried? 

## The Audit That Stopped at V1

 The conditions that made this exploit possible weren't hidden. 

 They were sitting in a verified contract, in a public permission registry, in an architecture with no gatekeeping on its most privileged path. Nobody came looking before the attacker did. 

 NMT's platform was audited by Burra Security in October 2025, a review of their V1 system, kept private at NMT's request.

 Burra Security, confirmed directly to Rekt News: "It was the V1 version of their system which did not have the vulnerable SquidRouterModule. Since our security review with them they made a bunch of changes and released V2 version of their contracts which included adding the SquidRouterModule."

 A module with two bypassable checks and one missing line, deployed to mainnet, granted full spending authority over client wallets, left running for three months.

 New Market Trading promises clients it will "never shy away from telling you where the dangers lie." 

 The danger was in their own code. 

 Frank Hepworth , founder and CEO of New Market Trading , runs a YouTube channel with a couple of dozen of videos on crypto strategy, onchain markets and more, including one titled "This Is How Smart People Get Rich with Crypto." 

 None of that translated into a second security engagement when V2 shipped with a new privileged execution path.

 NMT is not the first to learn this lesson in 2026, and not even the first this month.

 Over a week earlier, TrustedVolumes lost $5.87 million through an authorization boundary failure in a custom RFQ proxy - a permissionless signer registration function, a check against the wrong address, and unlimited approvals pointed at unverified code that had never been publicly reviewed. 

 One transaction. Four assets. Gone before most security firms had finished their alerts . 

 The pattern is close enough to be uncomfortable : Custom module, broken caller validation, no audit coverage on the vulnerable component.

 Safe modules are powerful by design, that's the point. Once enabled, they can execute transactions on behalf of the Safe without owner signatures.

 That capability is what makes automated DeFi strategies possible. It's also what makes an unreviewed module a complete and total drain vector for every asset the Safe holds.

 The victims didn't click a bad link. They didn't get phished. They onboarded to a wealth management platform, trusted its infrastructure, and had their funds swept by a contract that confused "I know who a valid delegate is" with "I am a valid delegate."

 On Tuesday May 27th, Frank Hepworth published an official statement on behalf of New Market Trading : 

 "The funds that were taken through the exploit belong to our clients - real people. We are offering a formal white-hat bounty - return 90% of the drained funds to the address below by Saturday 30th of May at 12AM EST, and we commit in writing to no prosecution and no civil action. You may retain 10% as recognition for identifying the vulnerability. We have notified relevant authorities and blockchain analytics firms, and onchain activity is being monitored. However, our priority is the recovery of funds for our clients. We urge you to do the right thing." 

 Return wallet: 
 0xeF9cbA776E050a552a8089498c5A3C69B89cE9DC 

 Contact via blockscan chat: 0xa7db9793d4978a26ee01c2a6cbf5ba154925a7532e31ae731f7f08ba4295ee70

 Read the official bounty post here: 

 Bounty Post 

 As of publication, no post-mortem published. No attacker response confirmed. The DAI hasn't moved so far. 

 When the module sitting between your clients and their funds skipped the audit queue, and the platform's selling point is security, what exactly was being sold? 

 Nobody phished NMT's clients. Nobody compromised a key. Nobody needed to. 

 The attacker read a public contract, copied a string, encoded a real delegate address from an open permission registry, and called a function that was never supposed to be a front door. 

 The architecture did the rest : Eighty-eight Safes, multiple fake token pools across three chains, one worthless token and then $3.98 million - converted, consolidated, and sitting untouched, while the platform that promised to protect it published a bounty page .

 Three months of open permissions . A V1 audit that never covered the module that failed. A Basescan name that sent an entire industry pointing at the wrong protocol .

 Squid had to publicly disown a contract they'd never seen. The CEO of Safe had to remind the world that modules enabled outside their official interface carry risks their tools can't surface. 

 Two innocent bystanders spent their day running damage control for someone else's unreviewed code. 

 The confused-deputy flaw at the heart of this, trusting payload data over msg.sender , is not a novel attack. It's a documented pattern. The kind of thing an audit is supposed to catch, the kind of thing a threat model is supposed to anticipate, the kind of thing that has drained protocols before this one and will drain protocols after it.

 $3,070,767.09 in DAI is sitting in a public wallet. The official bounty is open until May 30th .

 When your clients trust you with their wealth and the module guarding it shipped without a review, the exploit isn't the failure. The failure was everything that came before it.

 The attacker didn't outmaneuver anyone. They just read the source code. The clients never had a chance. 

 When the only thing standing between a wealth management platform and its clients' funds was a string anyone could copy, what exactly were they paying for? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

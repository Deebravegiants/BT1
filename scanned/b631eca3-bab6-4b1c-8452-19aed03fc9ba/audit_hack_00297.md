# [H] Wasabi Protocol exploit: Three minutes, over a dozen vaults, four chains, $5.9 million gone

## Summary
Severity: High
Target: Wasabi Protocol
Loss: $5,900,000
Published: 4/30/2026
Source: https://rekt.news/wasabi-protocol-rekt
Type: rekt-postmortem

## Details
## Wasabi Protocol - Rekt

 Monday, May 4, 2026 Private Key Leak - Wasabi Protocol - Single Point of Failure 

 read this article also in : 

 Three minutes, over a dozen vaults, four chains, $5.9 million gone . 

 In the early hours of April 30, an attacker who had already done the hard work, obtaining the private key to Wasabi Protocol's sole admin wallet , and pressed go. 

 What followed wasn't a hack in any technical sense. No vulnerability was found and no code was broken.

 The attacker simply used the key the way it was designed to be used, and Wasabi's entire vault architecture obeyed.

 The deployer EOA, wasabideployer.eth , held unchecked ADMIN_ROLE across every upgradeable vault Wasabi had ever deployed.

 No multisig shared that authority. No timelock slowed it down. No governance body had a vote. One wallet. One key. Total control. 

 Blockaid's detection system caught it live. 

 CertiK followed within minutes.

 The community watched on-chain as 840.9 WETH - roughly $1.9 million - left the vault in a single transaction, with seven other vaults emptied in the same block. 

 On Ethereum, Base, Berachain, and Blast, the same orchestrator ran the same playbook simultaneously .

 Wasabi's first public statement came hours after the drain began : Aware of an issue, investigating, don't touch the contracts. 

 ZachXBT and Cos had already framed the real story - this wasn't about a stolen key, it was about building a protocol where stealing one key was enough . 

 April 2026 has been the worst month for DeFi since records started mattering.

 Drift lost $285 million on April 1. KelpDAO lost $290 million on April 18.

 Wasabi adds to a month that has already produced over $635M in DeFi losses, and the pattern underneath every single one of them is not getting more complicated, it's getting more obvious. 

 How does an industry that has watched this exact attack execute over and over still ship protocols where a single private key is the last line of defense? 

 Credit: QuillAudits , Peckshield , Blockaid , CertiK , Francesco Andreoli , Wasabi Protocol , ZachXBT , Cos , Abdul , Hypernative , Cyvers , Blocksec Phalcon , Virtuals Protocol , genkisudo123 , TheBlock , Berachain , TRM Labs , The Defiant Blockaid moved first. 
 Early on April 30th, its exploit detection system flagged an active drain across Ethereum and Base, named the attacker EOA , identified the mechanism, and published the drain transaction hashes. It landed while most of Wasabi's users were asleep. 

 Extracted so far : ~$4.55M.

 Investigation ongoing. Those were the only numbers Blockaid had at that moment , Berachain and Blast hadn't yet been confirmed.

 Hypernative issued high-severity alerts almost an hour later , framing it as "Wasabi Perp Drained for ~$5M+ Across Three Chains via Deployer Key Compromise" - a wider lens already capturing what the others hadn't yet mapped.

 Cyvers flagged the Tornado Cash-funded attacker address and the ETH consolidation pattern. 

 Blocksec Phalcon published deep-dive transaction traces for both chains . 

 Wasabi's first public statement arrived over two hours after Blockaid's alert : "We're aware of an issue and are actively investigating. As a precaution, please do not interact with Wasabi contracts until further notice."

 No figure. No mechanism. No acknowledgment of the attacker EOA that three firms had already published.

 The chain had already told the story - 840.9 WETH gone from the wWETH vault, seven other vaults emptied in the same transaction, Base drained minutes later. 

 By the time Wasabi’s statement was posted , the funds were consolidating into ETH and routing toward distribution wallets. 

 Wasabi’s second update came roughly 3 hours after the first alert : "We've been working with professional security teams including SEAL-911 and Blockaid. Further updates will be shared as soon as they are available. Do not interact with Wasabi contracts until further notice."

 Two statements across three hours. Neither contained a loss figure, a transaction hash, or any technical detail that wasn't already visible on-chain.

 The community filled the gap.

 ZachXBT pointed at the EOA failure within the hour. 

 Francesco Andreoli published a breakdown : Mechanics, LP token warning, RevokeCash recommendation - before Wasabi had issued its second post. 

 PeckShield, confirmed what earlier estimates had missed : The attack had spread to Berachain and Blast.

 Total losses across all four chains : $5.9 million

 Blockaid's follow-up was more operationally urgent than anything the team published . It issued a direct warning to every wallet integrating Wasabi LP tokens - the underlying assets were gone, redemption value zero, and all Wasabi/Spicy LP-share tokens minted by the compromised vaults should be treated as "COMPROMISED" while the deployer key remained live.

 Virtuals Protocol, which had integrated Wasabi to let 50+ AI trading agents route leveraged positions , moved faster than the protocol itself. Before Wasabi's second statement had dropped, Virtuals froze all margin deposits powered by Wasabi , confirmed its own systems were unaffected, and warned users not to sign anything Wasabi-related.

 By the end of the day, no post-mortem had been published. No compensation plan existed. SEAL-911 was engaged. The contracts remained paused.

 The attacker's wallets, five addresses confirmed by QuillAudits, holding $5.9M in stolen funds , sat visible on-chain, until some exited into the abyss of Tornado Cash. 

 The funds were gone before Wasabi had finished typing, so why did one key have the power to send them there in the first place? 

## Pwned by Design

 Wasabi wasn't exploited. It was administered, by someone who had no right to be holding the keys. 

 At the center of everything sat a single externally owned account: wasabideployer.eth . 

 That wallet was the Wasabi Deployer EOA, used to grant ADMIN_ROLE to the attacker's helper contract , which then upgraded the perp vaults and LongPool to a malicious implementation that drained balances.

 Not one of several signers. Not a participant in a governance vote. The only one. Whatever that key said, the protocol did.

 Wasabi Deployer EOA: 
 0x5c629f8c0b5368f523c85bfe79d2a8efb64fb0c8 

 Attacker EOA: 
 0x02228b0afcdbEdf8180D96Fc181Da3AF5DD1d1ab 

 Attacker Orchestrator Contract (granted ADMIN_ROLE): 
 0x878E94142409DAFCC5CC83D5cD2e9DA2Bf0BF3bF 

 How the key moved from Wasabi's infrastructure to the attacker's wallet remains publicly unanswered.

 Phishing, malware, social engineering, insider access - every possibility is still on the table.

 What isn't in question is what happened once it did.

 The attacker called grantRole() from the deployer EOA with a single critical parameter : delay=0. 

 That zero is the whole story. No waiting period. No announcement window. No time for a user to see the pending action and exit. 

 The attacker's orchestrator contract became an admin instantaneously, inheriting the same authority wasabideployer.eth had held since the protocol launched.

 Grant role transactions hit all four chains in sequence. 

 Ethereum Grant Role Transactions: 
 0x985b4cde1075c67841d0f9fd897da34c9da53d77f6e23b5a19653ebff4a6fac1 
 0x11ff84ffbd62d2f4f26b289d79938a899967fb69f4ef40bf7f0e36ef295f1ded 

 Base Grant Role Transactions: 
 0x0b5dcdf9929b31ceffa1ac65aaba0cdd025296e09d9445d4767cf605f5ed52b7 
 0x185512ab15493ddd22a8b3fc94e0b095fbec0d0dbea0b97abebbdb9bcc8567a8 
 0xa2ec466f24b51e797fb74ce0462083fa5dba308469848446585450c39648ce2f 

 Berachain Grant Role Transaction: 
 0x23c5d80650fc49ed253e66833169a57f9a9553d358798ce50a8d56696c2ea363 

 Blast Grant Role Transaction: 
 0xbcb10b3d78bdeba47decf7693c81cb0562eeefc926902abc2a8eb5eeb641b542 

 With admin authority secured on every chain, the malicious orchestrator contract moved to the vaults . 

 WasabiVault proxies and the WasabiLongPool were upgraded via UUPS , Universal Upgradeable Proxy Standard, to malicious implementations the attacker had already prepared . 

 The legitimate vault logic was replaced entirely. What remained looked like a Wasabi vault. It was not.

 Then came strategyDeposit() . Each vault had a function that allowed an admin to direct its assets into an approved strategy contract, a legitimate mechanism for yield routing in normal operation.

 The attacker deployed a minimal fake strategy contract built purely to pass the validation checks inside strategyDeposit().

 strategyDeposit() accepted any destination . No whitelist. No post-call check that assets remained. The vaults had no way to know the difference. 

 A drain() function on the other end swept everything to the attacker EOA. The vaults weren't robbed. They were instructed to empty themselves. 

 On Ethereum, the attacker deployed the malicious orchestrator contract , looped strategyDeposit() across the vaults in a single transaction, and swept approximately $2 million, then ran the same pattern on Base for approximately $2.5 million, and on Blast, with losses still being reconciled at time of reporting.

 Largest single hit : 840.9 WETH, approximately $1.9 million, from the wWETH vault alone.

 Ethereum Vault Drain Transaction: 
 0xcd77423f1bfa362c43f98356360c1f6c6e5fe989f18036e874884e9ad4a70116 

 Ethereum LongPool Drain Transaction: 
 0xbabbfd5dc3a448244b1797928c69001726106c241f29e22b979a8bc01807c317 

 Base Vault Drain Transaction: 
 0x10b371603d42a672b0bffda526af8400885c65fa7b541678f2bd8dad6fcb7e40 

 None of this required a bug. None of it required a novel attack vector. The contracts performed exactly as written. 

 Francesco Andreoli put it plainly : "The Wasabi Protocol exploit isn't really a story about a stolen key. It's a story about what happens when one EOA controls a batch of upgradeable vaults with no multisig, no timelock, and no DAO governance." 

 A multisig would have required multiple signatures before grantRole() could execute . A timelock would have forced a delay - hours, days - between the role grant and its activation, giving users a visible window to react.

 Either one breaks the attack chain entirely.

 Wasabi had neither. The deployer key was the protocol, and once someone else held it, the protocol was theirs.

 Blockaid flagged something that sharpened the picture further : The attacker's orchestrator and strategy contract bytecode matched patterns from prior activity targeting Wasabi specifically. 

 This was not a scan-and-exploit operation running across every vulnerable protocol. Someone had studied Wasabi's architecture , prepared the contracts in advance, and waited for the key. 

 How long they had it before they used it is unknown.

 The funding transactions from the Tornado Cash-linked address, arrived in the late hours of April 29 , but preparation of the malicious contracts could have preceded that by days or weeks.

 The execution was too clean, too fast, and too precisely targeted to have been improvised. 

 Once the key was in the wrong hands, how long did it take to empty everything? 

## Drain, Convert, Disappear

 The groundwork was laid six hours before the drain. 

 On April 30th, at 01:12 UTC , the attacker EOA received 0.188 ETH from a Tornado Cash-linked address , the first funding transaction of the day, enough to cover gas. 

 Three more small top-ups followed between 07:07 and 07:36 UTC, each routed from the same cluster.

 By 07:46 UTC, the malicious contracts were deployed and the gas was loaded across chains. 

 At 07:49:47 UTC, on Ethereum, the vault drain executed.

 Eight vaults hit simultaneously. WETH, USDC, REKT, PEPE, MOG, HarryPotterObamaSonic10Inu, ZYN, NEIRO - everything each vault held was pulled into the attacker's fake strategy contract and swept in a single call.

 Ethereum drain - confirmed token amounts: 
 840.9 WETH.

 ~$172K USDC.

 400 billion REKT (no association with Rekt News).

 878 million PEPE.

 10 billion MOG.

 36,700 HarryPotterObamaSonic10Inu.

 458,000 ZYN.

 1,850 NEIRO. 

 Ethereum Vault Drain Transaction: 
 0xcd77423f1bfa362c43f98356360c1f6c6e5fe989f18036e874884e9ad4a70116 

 WETH unwrapping started immediately. Between 07:50 and 07:58 UTC, a sequence of conversion transactions turned the wrapped positions into native ETH as fast as blocks would allow. 

 Non-ETH tokens - PEPE, MOG, USDC, REKT and the rest - were swapped into ETH .

 Cyvers confirmed the pattern : Stolen funds consolidated into ETH, then distributed across multiple addresses. 

 At 07:53:11 UTC, the first large distribution moved. 300.2119 ETH left the attacker EOA and landed in hacker wallet #2. 

 300.2119 ETH → Hacker Wallet #2: 
 0x108e4fb1c62d8336d8e26bc58f545d1518c6b9bea8969cdff80b51692959dfde 

 Destination: 
 0xb8Bb8aDDd6b283be57b4635Bf913B34824ca70dB 

 On Base, the drain ran at 07:52:37 UTC , two minutes and fifty seconds after Ethereum, same attacker EOA, same playbook.

 Several vaults cleared: sUSDC, wWETH, sBTC/cbBTC, sVIRTUAL, sAERO, sBRETT, sWELL, sSKI. A second drain transaction hit additional vault contracts in the same window. 

 Base Vault Drain Transaction #1: 0x10b371603d42a672b0bffda526af8400885c65fa7b541678f2bd8dad6fcb7e40 

 Base Vault Drain Transaction #2: 0x6b18d05a77e6a9334e4a481671533d6d4cbed746a3c7ddc6ab7a096f09869626 

 Back on Ethereum, the LongPool went down at 07:59:35 UTC .

 The same malicious implementation that replaced the vault logic had been applied here too. 

 Two inbound transfers - 204.37 ETH and 22.07 ETH - arrived back at the attacker EOA at 07:59:55 and 08:01:11 UTC, proceeds from the LongPool drain routed after conversion. 

 Ethereum LongPool Drain Transaction: 
 0xbabbfd5dc3a448244b1797928c69001726106c241f29e22b979a8bc01807c317 

 At 08:01:11 UTC, 500 ETH left the attacker EOA in a single transaction and landed in hacker wallet #1. Combined with the 300 ETH dispatched eight minutes earlier, the bulk of the Ethereum-side haul had cleared the primary attack address before most of Wasabi's users had seen a single alert.

 500 ETH → Hacker Wallet #1 at 08:01:11 UTC: 
 0x9f54887999f3ccc8e97b3836248a788393c00f2f10bb04d8c64502fdbc104abd 

 Destination: 
 0x6244117E1B30101F2De25442211F6A92833Cf906 

 Smaller residual sweeps continued through the morning as the final token conversions cleared.

 By 09:07 UTC a further 28.19 ETH had moved outbound.

 The Dune dashboard built by genkisudo123 tracked 82 Ethereum transactions from the attacker EOA on April 30, with peak hourly ETH volume spiking between 07:00 and 09:00 UTC. 

 Five confirmed attacker wallets , all loaded within the same two-hour window: 

 Hacker Wallet #1 - 528 ETH: 
 0x6244117E1B30101F2De25442211F6A92833Cf906 

 Hacker Wallet #1 sent the 528 ETH on May 3rd to this address: 

 0x6ee7CF87647ea512Efb7516c2912f2ea65e6C305 

 Which sent the 528 ETH here, then exited some funds through Tornado Cash: 
 0x663e3250548A950b7c73AD4e6ae912d48cc4257F 

 The rest of the ETH was sent in smaller amounts to several addresses, which also exited through Tornado Cash.

 Hacker Wallet #2 - 300 ETH: 
 0xb8Bb8aDDd6b283be57b4635Bf913B34824ca70dB 

 Hacker Wallet #2 sent the 300 ETH on May 1st, to this address: 

 0x3015789366465d4C18654914E2133180b4bF2D7b 

 Which sent the 300 ETH here, then exited through Tornado Cash: 

 0x8bF50116AAA2876E1242591B1EdC5643CC281208 

 Hacker Wallet #3 - 500 ETH: 
 0x1A5B4A0bd3f572328AC7a8d7a3A96955F7ed2d95 

 Which sent ~500 ETH on May 2nd, to this address: 

 0x64239C20EA8e1b45F08c801CC66aE69AE94D51D9 

 Which sent the ~500 ETH here, then exited some funds through Tornado Cash: 
 0x621a7fD3010080db25bC951AD9E3B314e6Ed0fbc 

 The rest of the ETH was sent in smaller amounts to several addresses, which also exited through Tornado Cash.

 Hacker Wallet #4 - 500 ETH: 
 0x62ee357dd9170d85da8396765534f1bb01e13d86 

 Which sent ~500 ETH on May 4th, to this address: 

 0xc84F0FA1c2bE91DF6800cc37a70d89e5694f6dd4 

 Which sent the ~500 ETH here, then exited some funds through Tornado Cash: 
 0xFe4fD63467683D71c1B05FEC4F94c3b0599290E9 

 The shell game continued, as the rest of the ETH was sent in smaller amounts to several addresses, which also exited through Tornado Cash. 

 Hacker Wallet #5 - 737.36 ETH (only wallet still holding funds as of May 4th): 
 0xd48180d4697ce4b45a8056b0f3d716d10018ed03 

 $5.9M tracked across five addresses , four wallet moves and a Tornado Cash exit later, and most of it went into the abyss.

 Four of the five wallets have moved funds through Tornado Cash, each routed through intermediary addresses before exiting.

 Berachain and Blast were confirmed by PeckShield as additional drain targets, though granular token-level data for those chains had not been published in the same detail as Ethereum and Base at time of reporting.

 The $5.9 million figure from QuillAudits folds them in .

 With Berachain and Blast added to the total. The chain didn't lie, it just took time for the full picture to come into focus. 

 Five addresses, $5.9M, four already through Tornado Cash. When does the last one follow? 

## Open Ledger

 On May 1, Wasabi published its first substantive update. The breach had been contained. Access paths closed. Credentials and keys rotated. 

 An on-chain message had been sent to the address holding the funds, stating the team was open to a constructive resolution and urging the attacker to reach out privately. 

 Solana deployments and the Prop AMM were confirmed unaffected . A post-mortem was offered but not yet published .

 The attacker didn't wait for it. As they started to cash out in the meantime.

 The ecosystem didn't either.

 Berachain issued its own warning, advising users to withdraw funds immediately and estimating approximately $50,000 in user funds on its network were at risk. Reward vault operations were temporarily paused as a precaution. 

 Virtuals Protocol froze all margin deposits and confirmed its own systems were unaffected. 

 ZachXBT put the sharpest question on record: "Why did a single EOA seemingly have so much control without basic safeguards? Seems your runway was burned on KOL grifters like Kook…."

 Wasabi raised $3 million from Electric Capital in 2024 with a co-investor list that included Pudgy Penguins CEO Luca Netz, Magic Eden co-founder Zhouxun Yin, and a roster of prominent CT personalities.

 Whether the capital went toward security infrastructure is a question the team has not addressed. 

 A TRM Labs report released on April 30th, found North Korean state-backed hackers responsible for 76% of all global crypto hack losses in 2026, nearly $600 million, bringing their total since 2017 past $6 billion. 

 No formal attribution has connected Wasabi to that group. But DPRK sure had a busy month .

 As of time of publishing: Investigation ongoing, post-mortem pending, compensation plan nonexistent.

 Four of five wallets have moved through Tornado Cash. One wallet remains. 

 Wasabi had a working product, real volume, and $8.5 million in user deposits, none of it mattered when the key moved. A multisig would have. A timelock would have. So why weren't they there? 

 Nobody broke Wasabi's code. They took the key, and the code did everything it was designed to do. 

 That distinction matters, because it means no audit would have caught this, no bug bounty would have flagged it, and no amount of smart contract review changes the outcome when the most powerful role in the protocol lives behind a single private key with nothing standing between it and total control. 

 The vulnerability wasn't in the contracts. It was in the decision to build the governance that way in the first place.

 Drift was the first major incident of April - $285 million, a perpetuals protocol, a governance structure with no timelock, drained in minutes by attackers who had spent months earning the trust required to reach it.

 The mechanism was different. The failure mode was the same: One path to total control, no friction between access and execution, everything gone before anyone could respond.

 According to The Defiant , April 2026 ended as DeFi's worst month on record, $635 million lost across 28 incidents in 30 days . 

 Wait, make that 29 incidents . 

 Are we a bunch of April Fools?

 OpenZeppelin's TimelockController is free and open source. Gnosis Safe is free and open source. Both have been standard practice recommendations in DeFi security literature for years. Neither was present at Wasabi when it mattered.

 The $3 million seed round that funded this protocol had the backing of some of the most connected names in the space, none of whom appear to have made governance architecture a condition of the check.

 Four of five hacker wallets have already cleared through Tornado Cash. One wallet is still holding stolen funds. 

 The investigation is open. The post-mortem is pending. The compensation plan does not exist yet.

 And somewhere, in some other protocol's codebase, a single EOA is sitting on ADMIN_ROLE with no timelock, no multisig, and no governance layer between it and everything users have deposited. 

 Wasabi won't be the last protocol to find out what happens when one key is all it takes, so who's next, and do they already know it? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

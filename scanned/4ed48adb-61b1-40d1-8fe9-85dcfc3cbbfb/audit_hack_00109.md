# [H] GANA Payment exploit: Nine days is all the trust you get in DeFi these days

## Summary
Severity: High
Target: GANA Payment
Loss: $3,100,000
Published: 11/20/2025
Source: https://rekt.news/gana-payment-rekt
Type: rekt-postmortem

## Details
## GANA Payment - Rekt

 Tuesday, November 25, 2025 GANA Payment - Admin Privileges - Rekt 

 read this article also in : 

 Nine days is all the trust you get in DeFi these days. 

 GANA Payment's freshly minted payment protocol on BNB Smart Chain lost $3.1 million before users could stake anything meaningful. 

 The attacker didn't need sophisticated exploits or oracle manipulation - just an EIP-7702 delegator contract and someone's leaked owner key , turning the staking mechanism into a personal ATM through repetitive stake-unstake loops.

 Launched November 11th , exploited November 20th.

 No audit. No time to build trust. No chance to prove the tech worked. 

 Token holders watched 90% of their value evaporate as funds scattered across chains - $2.1 million bridged to Ethereum, the rest laundered on BSC, most already through Tornado Cash while 346 ETH sat dormant, waiting for its turn.

 ZachXBT flagged the carnage first , with Quill Audits and Blockscope dissecting the wreckage as the laundering continued in calculated batches. 

 When your protocol dies faster than a TikTok trend, who's really testing the code - developers or attackers? 

 Credit: TheBlock , Quill Audits , GANA Payment , ZachXBT , Blockscope , Ye in Web3 , BitcoinEthereumNews , GoPlus Security , Hacken , Coin Edition , DefiLlama , Seedify , SlowMist , Yahoo Finance , DexScreener 
 ZachXBT broke the news in the wee early morning hours on November 20th , posting the consolidation address while most of crypto Twitter was still asleep. 

 By the time GANA Payment posted their "urgent announcement" acknowledging the breach , the attacker had already deposited 1,140 BNB ($1.04 million) into Tornado Cash on BSC and started bridging the rest to Ethereum.

 "GANA's interaction contract has been targeted by an external attack, resulting in unauthorized asset theft."

 Was it corporate speak for "someone with the keys emptied the vault?" 

 The team promised an emergency investigation with a third-party security firm , a comprehensive reboot plan, and full asset mapping. Standard crisis protocol - investigate, promise, rebuild.

 But the comments section may have told a different story : "Guys it's not 'interaction contract' was targeted it was private key leakage (at least)." 

 When your own community calls out the euphemisms before the investigation even starts, what exactly is there left to investigate? 

## EIP-7702: From Feature to Folly

 SlowMist founder Yu Xian cut through the noise : owner private key leaked, EIP-7702 delegator exploit deployed, onlyEOA check bypassed. 

 No hack needed. No market manipulation. Just full control handed over. 

 Because, someone had the keys.

 EIP-7702 was supposed to make Ethereum accounts smarter - letting externally owned accounts temporarily behave like smart contracts.

 Batch transactions, sponsored gas, delegated permissions.

 GANA's attacker turned that innovation into an exploitation framework. 

 The malicious delegator contract became the middleman between the compromised owner key and GANA's staking contract. 

 Malicious Delegator Contract: 

 0x7A44bD9C6095Ca7b2A6f62FE65b81924c6cAb067 

 GANA’s Staking Contract: 
 0xACF753d5d81462db45b7f024e9fa76993ce9bcfb 

 GoPlus Security suggests the attacker may have gained admin access via social engineering/phishing , then used transferOwnership to rotate through eight pre-prepared addresses , each one authorizing the EIP-7702 delegator to bypass the onlyEOA restriction that should have protected the unstake function.

 Hacken's analysis showed the pattern : stake GANA and USDT through seven different accounts, then withdrew tokens via a delegated contract using an EIP-7702 transaction.

 Just before the withdrawal , they manipulated the reward logic by setting an enormous rate for gana_Computility: 10,000,000,000,000,000

 Eight iterations. One systematic drain. 

 Primary consolidation address collected the pieces: 
 0x2e8a8670b734e260cedbc6d5a05532264aae5c38 

 The protocol's own systems couldn't tell the difference between legitimate rewards and manufactured theft - because to the smart contract, someone with owner privileges was just doing their job. 

 When your security model assumes the admin won't rob you, what's the difference between authorization and exploitation? 

## The Laundering Express

 The attacker didn't waste time admiring the haul. 

 Victim Staking Contract: 
 
 0xACF753d5d81462db45b7f024e9fa76993ce9bcfb 

 Malicious EIP-7702 Delegator: 
 
 0x7A44bD9C6095Ca7b2A6f62FE65b81924c6cAb067 

 Key Attack Transactions are as follows… 

 Ownership Transfer (just before the drain): 
 0x8f909383a91c55282a59a1568a9ca58f7e4a02d26f1918dfc5c641a99bdabda8 

 Example Stake Transaction: 
 0xac935e62f3f6f375d856775f8fe2628e92b1944b15a251090bef213dc5f5f9e2 

 Main Exploit Transaction (unstake/delegator combo): 
 0x0a1fabbb536cf776335e2ded5ebf70f4c9601376e7265a127afe55305eff69ad 

 Primary BSC Consolidation Address: 
 0x2e8a8670b734e260cedbc6d5a05532264aae5c38 

 All roads led here first. The attacker swapped stolen tokens into liquid assets, then split the laundering operation across two chains. 

 BSC Route: 
 1,140 BNB (~$1.04M) → Tornado Cash on BSC .

 Fast, efficient, gone. 

 Secondary BSC Address (Handled remaining ~$1M before Tornado): 
 0xd10Ed57534Dc63f2ea9dC0cB0096086F3CC8fA4d 

 Then the bridge jump - roughly $2.1M moved to Ethereum via deBridge and Stargate.

 Initial Landing Address on Ethereum: 
 
 0x5149A7696188F083297281D10293a20476252CDD 

 Distribution Wallets ( flagged by Blockscope ): 
 0x7a503e3ab9433ebf13afb4f7f1793c25733b3cca 
 0x98fc13632ff112e4667fc4f21ae980571f122b5a 

 346.8 ETH ($1.05M) → Tornado Cash on Ethereum .

 But this wallet kept 346 ETH dormant for hours: 
 0x7a503e3ab9433ebf13afb4f7f1793c25733b3cca 

 Then the incremental laundering began - 1 ETH, 10 ETH, 100 ETH batches through Tornado Cash. The slow drip designed to shake off security researchers tracking the flow.

 Two chains, a little mixer action, throw in some calculated patience. And poof, money gone.

 The blockchain recorded every hop, every swap, every mixer deposit - a perfect ledger of theft that leads nowhere prosecutors can follow. 

 If the system does exactly what it’s told, who’s responsible when it’s exploited? 

## BSC's Trust Deficit

 GANA Payment launched November 11th , with no public audit and no security documentation . 

 9 days later, it joined BSC's growing graveyard of mid-sized exploits . 

 The numbers tell the story: 41% audit rate for smart contracts deployed on BSC in 2025 .

 Ethereum? 74% .

 That 33-point gap costs money.

 According to DefiLlama’s hacks tracker - BSC projects lost over $200 million to exploits in 2025 alone. 

 KiloEx , Seedify , GriffinAI and Woo X to name a few. Phemex alone lost $85 million and Nobitex got rekt for $82 million . 

 Now add GANA Payment as the latest victim on the network.

 Another protocol, another rinse‑and‑wipe on the chain.

 The playbook doesn't change because it doesn't need to.

 BNB Chain celebrated a 70% reduction in losses - $161 million in 2023 down to $47 million in 2024. 

 Progress, sure. 

 But 2025 erased all of it. Over $200 million lost across twelve exploits - more than quadruple 2024's total, proving the audit gap and governance problems never went away.

 GANA Payment's token crashed 90% within 24 hours. DexScreener charts showed the cliff - $2.98 to $0.31 as holders realized their payment protocol was paying someone else.

 The GANA Foundation announced their November 24th reboot plan : 100% of capital secured for ecosystem recovery, token bottom pool reconstruction, detailed compensation framework.

 Classic post-exploit theater - promise everything, deliver timelines, hope the news cycle moves on.

 But here's what the reboot plan doesn't address: how a protocol launched without an audit, compromised within 9 days, and drained through a well-known exploit pattern gets a second chance at user funds. 

 When speed-to-market beats security-by-design every time, who's really getting rekt - projects or their users? 

 9 days from launch to liquidation - GANA Payment set a new speed record for trust destruction. 

 $3.1 million gone before the documentation was even finished. 

 Before the first audit could be done . Before users had time to understand what they were staking in.

 EIP-7702 became the weapon. Private key compromise became the ammunition. Eight ownership rotations became the trigger mechanism.

 Someone with access decided the vault belonged to them, and the smart contract had no choice but to agree. 

 The blockchain recorded every transaction with perfect accuracy - ownership transfers, inflated reward rates, systematic drainage, cross-chain laundering. 

 GANA promises a reboot. Capital secured. Token pool reconstructed. Compensation planned.

 But compensation doesn't answer the fundamental question: why should anyone trust version 2.0 of a protocol that couldn't survive version 1.0 for 9 days?

 DeFi was supposed to eliminate the need for trusted intermediaries - instead, we've just created faster ways to discover which intermediaries shouldn't be trusted. 

 How many nine-day experiments with user funds does it take before "launched too fast" becomes indistinguishable from "launched to fail"? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

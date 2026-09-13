# [H] TMXTribe exploit: Thirty-six hours is plenty of time to stop a bleeding protocol – or plenty of time to let it bleed out

## Summary
Severity: High
Target: TMXTribe
Loss: $1,400,000
Published: 1/5/2026
Source: https://rekt.news/tmztribe-rekt
Type: rekt-postmortem

## Details
## TMXTribe - Rekt

 Thursday, January 8, 2026 TMXTribe - Logic Bug - Defi 

 read this article also in : 

 Thirty-six hours is plenty of time to stop a bleeding protocol – or plenty of time to let it bleed out. 

 TMXTribe, a GMX fork promising perpetual futures trading on Arbitrum, watched $1.4 million drain through unverified contracts while the team offered bounties , upgraded contracts, and did everything except the one thing that might have helped: hitting pause. 

 An exploit loop that turned minting and staking logic into a systematic drainage pump .

 No security audit to be found anywhere either.

 Thirty-six hours of active exploitation without a single emergency pause. 

 Then funds bridged to Ethereum via Across and disappeared into Tornado Cash .

 As of 4 days after the exploit, TMX has not said a word about it publicly.

 No post-mortem, no user compensation plan, no acknowledgment on their Twitter account that $1.4 million just walked out the door. 

 Was this incompetence so profound it became indistinguishable from malice, or malice so brazen it disguised itself as incompetence? 

 Credit: Defimon Alerts , CertiK , Extractor by Hacken , QuillAudits 
 DefimonAlerts flagged the first signs of trouble on January 5th , "GMX fork TMXTribe has been hacked on Arbitrum." 

 CertiK Alert flagged it hours after the drainage started : an unverified contract with a fatal flaw in its LP staking and swapping mechanics.

 The attack pattern was methodical : 

 Mint and stake TMX LP tokens using USDT. 

 Swap the deposited USDT for USDG (the protocol's internal stablecoin). 

 Unstake the LP tokens. 

 Sell/drain the acquired USDG. 

 Repeat. 

 No complex flash loan choreography. No oracle manipulation. No re-entrancy tricks. 

 Just a loop that the contract's logic couldn't detect, couldn't stop, and couldn't prevent from running again.

 And again.

 And again.

 The exploiter's address – labeled "Tribe Perpetual Exploiter" on Arbiscan – executed this sequence across 36 hours. 

 The root cause? Flawed logic in how the unverified contract handled minting, staking, and swapping. No checks. No balances. No circuit breakers. 

 Just open doors and an attacker patient enough to walk through them systematically.

 QuillAudits later documented what every security researcher already knew: unverified contracts are time bombs. You can't audit what you can't see. You can't trust what you can't verify.

 TMXTribe may have chosen to deploy critical infrastructure without verification. Without an audit. Without the basic hygiene that separates legitimate protocols from exit opportunities.

 The result? $1.4 million in systematic drainage across 36 hours while the team watched, deployed contracts, and did everything except hit pause or even publicly acknowledge that they have been exploited. 

 When your smart contract logic treats exploit loops like valid transactions, is it really a hack or just a withdrawal with extra steps? 

## The Stolen Loot Trail

 The attack didn't need complexity to succeed, just an unverified contract with no guardrails. 

 The exploiter's main address executed the systematic drainage loop across 36 hours, converting stolen assets into ETH. 

 Exploiter Address (Arbitrum): 

 0x763a67E4418278f84c04383071fC00165C112661 

 Initial Funding Transaction (January 3rd): 0xaa789bba4dbf761f427de69277fcdeaaa75894f219e2bb44c6fcf40eb68d95d8 

 Over the next 48 hours, the exploiter address would execute 502 transactions , systematically dismantling TMXTribe's liquidity.

 Internal transactions showed the extraction pattern : convert drained assets to ETH, batch them, prepare for bridging.

 Some of the most notable transactions were systematic batches of 94.13 ETH ($309,451), 62.57 ETH ($205,704), 57.47 ETH ($188,945), and 47.05 ETH ($154,697) moving through the blockchain like clockwork, each representing hundreds of thousands in stolen funds finding their exit route. 

 Secondary Exploiter Address: 

 0x16Ed3AFf3255FDDB44dAa73B4dE06f0c2E15288d 

 This address ran the same exploit loop in parallel. Token transfers show it minting TMX LP with USDT, swapping for USDG, unstaking, and draining repeatedly – the identical attack pattern playing out on a second front.

 All roads led to Ethereum, but not directly to Tornado Cash. First came Across Protocol – the bridge that would move the stolen funds off Arbitrum. 

 Bridge Transaction 1 (260 WETH - $821k): 

 0xa060241eaee611c801c043fd38bac7e0d979e76106b64c2ad431f628a4a64e16 

 Bridge Transaction 2 (3.419912 WBTC - $312k): 

 0xf003f6f833dca32dff39697f3bcee4875b7e45d61cf3ba9cd5bab66011ed3e60 

 Bridge Transaction 3 (15.939846 WETH - $50k): 

 0x6a845d0971b9c4255797530d93257318cfa8bcd04d680490c15b9573316c0d0d 

 Once on Ethereum, the funds landed at the original exploiter’s address – just under $1.2 million in stolen assets ready for the final step.

 Then came Tornado Cash. The exploiter systematically deposited the stolen ETH into the mixer , obscuring the trail. The standard final step for anyone who knows they're never returning a single dollar.

 By the time security researchers were documenting the exploit, the money was already gone. Not hidden in some warm wallet waiting to be negotiated. Not sitting in exchanges that might freeze assets. 

 Gone. Atomized into Tornado Cash's privacy fog. 

 Exploiter's Current Balance: 0.00664 ETH (~$21)

 Everything else: Laundered, mixed, untraceable.

 Extractor by Hacken tracked it all in real-time . Funds bridged to Ethereum. Deposited to Tornado Cash. Standard operating procedure for someone who knew exactly what they were doing and had zero intention of returning anything.

 The blockchain remembers every transaction, but Tornado Cash makes sure nobody can follow them home. 

 When the money's already in the mixer, what exactly are you negotiating for? 

## Too Little, Too Late, Too Gone

 While the funds were bridging to Ethereum and disappearing into Tornado Cash, TMXTribe finally made a move. 

 Not a pause. Not a circuit breaker. Not an emergency shutdown. 

 Instead they sent a message.

 On-chain, the team reached out to the exploiter addresses with a standard bounty offer : Keep 20%, return 80%, and we'll call it even.

 The plea, permanently inscribed on Arbitrum for anyone to read: 

 0xb31a0e8b0ed3a370493f6f63c01600cee62e1d4df2af159c9ff22fc2d8adccf4 

 The exploiter's response? Silence. Not even the courtesy of a "no." 

 Meanwhile, the blockchain tells a different story. 

 Because the wallet that sent the bounty message: 

 0x33392e39325013e81874ca7b76326858ec179543 

 And also spent some time deploying contracts.

 January 5th, 7:02 AM UTC - the first contract deployment creates a new contract: 

 0xb4c0631e40d0be8aa0f53baf886530c36ab36aac2591c2d1dbcf237e158b2565 

 Immediately followed by an upgrade transaction targeting the following contract: 0x3AfdbeF553d5c92817da37096bb2e47daeEF951d 

 The contract deployments continued on January 5th… 

 10:49 AM: Another contract deployed .

 10:49 AM: Another Contract Upgrade (Targeting the same contract as the 1st upgrade transaction).

 10:49 AM: Yet another Contract Upgrade (Targeting the same contract as the 1st upgrade transaction).

 12:08 PM: Another contract . Another upgrade .

 1:46 PM: The bounty message goes out to the exploiter .

 1:57-8 PM: Another contract created . Two more upgrades were executed.

 Upgrade 1 

 Upgrade 2 

 2:16 PM: Another contract deployment . Another upgrade .

 2:19 PM: Another contract deployment . Another upgrade .

 3:06 PM: Another contract deployment . Another upgrade .

 3:06 PM: Another contract deployment . Another upgrade .

 Then 2 days later on January 7th, between 7:50 AM and 7:51 AM UTC: Another Contract created , followed by 2 upgrades.

 Upgrade 1 

 Upgrade 2 

 The team wasn't absent. They were present, active, deploying contracts and executing upgrades throughout the 36-hour window. What they weren't doing was the one thing that might have stopped it: hitting pause. 

 Every upgrade transaction is visible on Arbiscan . Every contract deployment timestamped and permanent.

 The evidence doesn't show a team scrambling after the fact – it shows a team working methodically through an exploit they apparently couldn't or wouldn't stop.

 And here's the strangest part: that wallet is still active . Not abandoned. Not gone dark. Still operational.

 So what were they upgrading? What were they building while the protocol hemorrhaged $1.4 million? And why deploy contract after contract, upgrade after upgrade, without once triggering an emergency pause? 

 Thirty-six hours of active exploitation. Thirty-six hours of watching funds drain. Thirty-six hours without implementing the most basic defense any DeFi protocol should have: an emergency pause function. 

 No circuit breaker triggered. No admin intervention. No attempt to halt the bleeding until it was far too late to matter.

 Extractor by Hacken could not have stated it better with brutal clarity : "exploit was ongoing for about 36 hours and TMX have not taken any actions to contain it."

 But the blockchain says they were taking actions. Just not the ones that would have saved user funds. 

 While the funds were already gone, the team's wallet kept working . Kept deploying. Kept upgrading contracts. 

 Still active days after the exploit.

 The protocol's communication? Silent.

 Their original TMXTribe account was deleted when checking on January 6th, but popped back up on January 7th, with one tweet , and a suspicious link that gets flagged as a likely phishing link .

 Meanwhile, their other Twitter account TMXdex remains active – just posting nothing about the $1.4 million dollar hole in their treasury.

 The wallet speaks. The contracts deploy. The upgrades execute. But the words? Those stay locked behind a silence that somehow says more than any statement could. 

 When you're present enough to upgrade contracts but absent enough to never explain why $1.4 million vanished, what exactly are you present for? 

 Sometimes the line between catastrophic incompetence and calculated exit is too blurred to matter. 

 TMXTribe had every warning sign blinking red before a single dollar was stolen: unverified contracts, no security audit, a GMX fork that inherited none of GMX's security rigor. 

 Then came the 36-hour exploitation window where the team did everything except stop it.

 The bounty offer was sent while funds were already mixing.

 The contract upgrades deployed while the protocol bled. 

 Was the negotiation the math of damage control or a mirage?

 Days later: No statement, no compensation plan, no accountability – just digital ghosts and $1.4 million worth of lessons written in immutable transaction logs.

 The blockchain recorded everything except the one thing that would have answered all the questions – and maybe leaving that question unanswered was the whole point. 

 When the code is open-source but the explanation stays closed, who's really benefiting from decentralization? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Rho Market exploit: An oracle's misconfiguration turns into a $7.5 million windfall for an alert MEV bot

## Summary
Severity: High
Target: Rho Market
Loss: $7,500,000
Published: 07/19/2024
Source: https://rekt.news/rho-market-rekt
Type: rekt-postmortem

## Details
## Rho Market - Rekt

 Friday, July 19, 2024 Rho Market - REKT 

 read this article also in : 

 An oracle's misconfiguration turns into a $7.5 million windfall for an alert MEV bot. 

 What began as a simple misstep in Rho Market's oracle configuration turned into a payday for an opportunistic MEV bot on July 19th, as it swiftly seized upon the opening within the protocol built on Scroll. 

 In the high-stakes world of DeFi, even the slightest miscalculation can lead to catastrophic losses.

 Millions can vanish in the blink of an eye.

 In this digital Wild West, MEV bots are the new gunslingers, their algorithms primed to outdraw any protocol that leaves its vault unlocked.

 But when the quick-draw artist holsters their gun and offers to return the loot, who's really the outlaw in this digital frontier? 

 Is it still an exploit if the attacker offers to give it all back? 

 Credit: CJ the "Doughnut" , ZachXBT , Scroll , Rho Markets , DefiLlama , Sudo , Miszke 
 Oracles are the eyes and ears of smart contracts, providing crucial off-chain data to on-chain systems. But when these digital soothsayers falter, chaos ensues. 

 According to DeFiLlama , Rho Markets is a fork of Compound Finance and held approximately $38 million worth of assets shortly before the exploit.

 Compound itself was at the heart of last week’s panic over the wave of front-end hijacking incidents on popular DeFi platforms.

 Rho Market's oracle misconfiguration allowed an MEV bot to manipulate price data, creating an arbitrage opportunity that drained $7.5 million from the protocol in a matter of minutes.

 First reported by CJ the “Doughnut”, who noted that the platform was drained of USDC and USDT. 

 CJ linked to the possible attacker’s address , which showed a gain of $7.5 million over the past hours. 

 Rho Markets acknowledged the unusual behavior and paused the platform.

 The incident prompted Scroll, the L2 network hosting RhoMarket, to temporarily halt the chain .

 ZachXBT highlighted that “Exploiter has a ton of exposure to centralized exchanges so would say there’s a good probability this gets recovered and they are gray or white hat.”

 Zach was not too far from the mark, as he shared an on chain message shortly after: 

 “Hello RHO team, our MEV bot have profited from your price oracle misconfiguration. We understand that the funds belong to users and are willing to fully return. But first we would like you to admit that it was not an exploit or a hack, but a misconfiguration on your end. Also, please provide what are you going to do to prevent it from happening again?” 

 They honored their word and the funds were returned shortly after.

 Rho Markets confirmed that the issue was resolved, without any loss of funds and they are currently reassigning funds back to the borrow pools.

 In response to the recent events, Rho Markets has outlined the following three-step plan: 

- 
 Identify accounts that supplied funds during the oracle malfunction.

- 
 Replenish the USDC, USDT, and wstETH pools to restore affected balances.

- 
 Reinstate borrowing and transfer functionalities while adhering to strict security protocols.

 While a prior security audit had identified potential vulnerabilities in the protocol's oracle implementation, the incident stemmed from a human error during deployment rather than a code flaw.

 In a space where censorship-resistance and permissionless are more than just buzzwords, incidents like these force us to confront uncomfortable truths about the current state of blockchain infrastructure. 

 While Rho Market dodged a bullet this time thanks to a benevolent bot operator, will the next white hat be so generous? 

 The recent DeFi debacle not only exposed oracle misconfiguration issues but also reignited the debate on decentralization in Layer 2 solutions. 

 As Rho Market's blunder prompted Scroll to halt its chain, Sudo pointed out that L2s touting permissionless and censorship-resistant values are merely posturing to attract VC money, making L1 Ethereum's genuine decentralization all the more appealing. 

 L2 operators now face a catch-22, censor to save funds and risk centralization accusations or stay true to permissionless ideals at the users' expense.

 With centralized sequencers and provers becoming common on L2s, liability concerns grow as operators potentially become centralized failure points vulnerable to legal and regulatory pressure.

 While Layer 2 solutions promise scalability and decentralization. 

 Are we building a censorship-resistant future or just creating a more efficient version of the systems we aimed to replace? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

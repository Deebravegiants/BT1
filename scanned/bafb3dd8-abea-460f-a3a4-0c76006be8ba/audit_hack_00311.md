# [C] Yieldblox exploit: $10.97 million gone from YieldBlox's community-managed pool on Blend V2, and all it took was one trade in the USTRY/USDC market with less than $1 in h

## Summary
Severity: Critical
Target: Yieldblox
Loss: $10,970,000
Published: 2/22/2026
Source: https://rekt.news/yieldblox-rekt
Type: rekt-postmortem

## Details
## Yieldblox - Rekt

 Friday, February 27, 2026 Yieldblox - Blend V2 - Oracle Manipulation 

 read this article also in : 

 $10.97 million gone from YieldBlox's community-managed pool on Blend V2, and all it took was one trade in the USTRY/USDC market with less than $1 in hourly volume. 

 No novel bug, no smart-contract sorcery, just liquidity vaporized the old-fashioned way .

 Someone found a collateral asset so thinly traded that fewer than five tokens sat on the ask side of the order book , and they pumped the price 100x with a single transaction .

 The Reflector oracle dutifully reported the new price . Blend V2 dutifully accepted the collateral valuation . The attacker dutifully borrowed $10.97 million in XLM and USDC and walked out the door.

 YieldBlox has been building on Stellar since 2022 . Script3 , the team behind it, ran a community-managed pool on Blend V2 . 

 USTRY, a yield-bearing US Treasury stablebond from Etherfuse , was listed as eligible collateral . 

 The attacker deposited ~153,000 USTRY in two rounds , worth roughly $160k at real prices, and borrowed against it as though it were worth $16 million . USTRY was never stolen. It was the key. The XLM and USDC sitting in the pool were the loot.

 Nobody had put a floor on what kind of market conditions that collateral needed to actually hold its value.

 Tier 1 Validators scrambled to freeze 48 million XLM - about 80% of the stolen native token. The Security Council sent an on-chain bounty message. The attacker's response was to keep laundering. 

 When the USTRY/USDC market on the SDEX had less than a dollar in hourly volume and YieldBlox's oracle treated its spot price like gospel - who exactly failed the security review? 

 Credit: DK27ss , Defimon Alerts , PR Newswire , QuillAudits , Script3 , Reflector , saariuslystoned , Code4rena , Certora 
 At 00:25 UTC on February 22, 2026, two transactions hit the YieldBlox DAO Pool on Blend V2. 

 The first borrowed 1,000,196 USDC . The second borrowed 61,249,278 XLM . Combined, $10.97 million drained in the time it takes to confirm two blocks.

 Security monitoring accounts caught the on-chain movement early, with DefimonAlerts posting attacker addresses and transaction links as the funds were still moving.

 But the first named team response came from Script3 , the team behind both YieldBlox and Blend: 

 "At 00:25:00 UTC the Reflector USTRY oracle was manipulated, misreporting a significantly higher price. This resulted in a loss of ~10 million USD in a mixture of USDC and XLM from the Blend YieldBlox pool. NO OTHER BLEND POOLS WERE AFFECTED. NO OTHER POOLS ARE VULNERABLE." 

 Short. Controlled. And notably specific about the blast radius, or the lack of one.

 Reflector, the oracle provider, followed with their own thread , but only after holding back until most of the stolen funds were frozen.

 Their statement walked a careful line : The infrastructure wasn't compromised, the oracle reported what the SDEX was actually showing, and the root cause was a market so illiquid it was impossible to price fairly.

 In Reflector's framing : "it’s impossible to quote adequate prices for a market fully handled by a single market-maker with almost zero trading activity." 

 The oracle did what the market told it to. The question nobody asked was whether that market was worth trusting. 

 Script3 clarified further on February 23 , confirming the attack was isolated to a single asset in a single community-managed pool, that Blend's smart contracts had no vulnerabilities.

 They followed up with a statement , that all depositors - USDC, XLM, and EURC - would be fully compensated for losses caused by the bad debt.

 The PoC that fully documented the exploit mechanics , complete with on-chain evidence, poisoned oracle entries, and health factor calculations, was published publicly on GitHub by DK27ss shortly after, leaving nothing to the imagination about how cleanly the attack had been constructed.

 YieldBloxDAO, the DAO's own X account , offered one update: A repost of Script3's compensation announcement . No original statement. No acknowledgment of what happened or how.

 Two teams. One exploit. Two very different explanations for who owned the failure. 

 When the oracle says it quoted correctly and the protocol says it was manipulated, who actually had the keys to prevent this? 

## One Trade. Four Failures

 USTRY was supposed to be safe collateral. A yield-bearing stablebond backed by US Treasuries, designed to trade at approximately $1.06. 

 Boring by design. The kind of asset that belongs in a lending pool. 

 What didn't belong was the market it lived in.

 The USTRY/USDC pair on the SDEX had less than $1 in hourly trading volume . Fewer than five USTRY tokens sat on the ask side of the order book .

 The market had no meaningful depth and effectively a single market maker , a market so thin that there was no competing activity to anchor the price .

 For at least 10 minutes before the exploit executed, there were zero trades . The market wasn't thin, it was a ghost town with a price tag on the door. 

 The Reflector oracle uses a VWAP model , volume-weighted average price, pulling directly from SDEX trading activity. 

 In a liquid market, VWAP is a reasonable approach, manipulated trades carry little weight against the aggregate volume of legitimate activity.

 In a thin market, a single trade with outsized volume dominates the calculation. In a market with no other activity, that trade's price is the VWAP.

 The attacker placed a sell offer at 100x the real price and bought against it, a single trade that pushed USTRY from ~$1.06 to ~$106.74 . With nothing else in the window to dilute it, that price became the oracle's truth.

 The PoC's decoded on-chain diagnostics showed what happened in real time. 

 Four price entries came back for USTRY. Two were flagged by the PoC researcher as SDEX-POISONED at $106.74. Two were normal at $1.06. 

 The Oracle Adapter, the contract sitting between Reflector and Blend, didn't take a median. Didn't flag the deviation. It returned the latest price and passed the full 100x inflation straight through to the pool.

 That's where the second failure compounded the first. Blend V2's health factor system did exactly what it was built to do, it checked whether collateral value exceeded liability value before approving a borrow.

 With USTRY priced at $106.74 , the pool valued the attacker's USTRY collateral position at $1.37 million .

 At the real price, it was worth ~$13,654, with a health factor of 1.35 and still, the borrow was approved. 

 The attacker went back for seconds. After depositing an additional 140,000 USTRY , the same poisoned oracle valued the total collateral at ~$15.99 million . 

 Real value : ~$158,500.

 Health factor : 1.47.

 The pool handed over 61,249,278 XLM without a second question.

 No circuit breaker fired. No price deviation check triggered. No staleness flag raised on a market that had been dead for ten minutes. The protocol had no mechanism to distinguish between a price that was accurate and a price that was accurate only because nobody had traded in long enough to correct it.

 Four distinct layers collapsed in sequence - illiquid collateral listing, a single-source VWAP oracle, an adapter returning raw last price, and a protocol with no anomaly detection. Remove any one of them and the exploit doesn't work. All four were present, and nobody had asked whether they could fail together .

 Not a smart contract bug. Not a flash loan. Not a bridge compromise. Just a stablebond with no market, an oracle with no guardrails, and a lending pool that trusted both. 

 Was this a failure of the oracle, the protocol, or the people who decided a ghost-town market was good enough collateral? 

## The Ledger Doesn’t Lie

 The attacker had a plan. The blockchain kept receipts. 

 Every address. Every transaction. Every token accounted for. 

 This exploit didn't start at 00:25 UTC. It started eight days earlier, when the attacker's primary Stellar wallet was created on February 14 with a 56.32 XLM seed.

 What followed was a few days of quiet reconnaissance, small USTRY test buys at normal prices around $1.058 , learning the market before breaking it.

 The price manipulation itself required a second, dedicated burner account, created on February 21 at 23:35 UTC with 15 XLM:

 SDEX Manipulation Burner: 
 GCNF5GNRIT6VWYZ7LXUZ33Q3SR2NUGO32F5X65VVKAEWWIQCKGYN75HB 

 This account existed for one purpose. At 23:38 UTC, it placed a sell offer for 1.2185 USTRY at 107 USDC - 100x the real price . 

 The offer transaction: 
 09e1a9d1197c9bf0af4e87da328c4f2d5eb49b487630aa61991fb5c1c4637cdb 

 Placing the offer wasn't enough - a trade had to execute for the oracle to read it. A third attacker-controlled account handled that. 

 Price-Setting Trade Trigger: 
 GDHRCQNC64UVL27EXSC6OG6I2FCT4NWM72KNHLHKEB3LK4MEEYYWETN3 

 At 00:10:21 UTC on February 22, this account bought 0.05 USTRY against the burner's inflated sell offer. That 50-cent trade became the market price the Reflector oracle ingested at 00:15 and 00:20 UTC.

 Price-setting trade transaction: 
 60fe039e96e88402d175c8de68e80651874ab125880dd384a1636914ba95bef1 

 With the oracle poisoned across two consecutive windows, the borrow executed at 00:24:27 UTC. Two transactions. Two assets. One protocol drained. 

 USDC Borrow (1,000,196 USDC): 
 ae721cacee382bdecac8d2c47286ecd42cb4711f658bb2aec7cba60dc64a31ff 

 XLM Borrow (61,249,278 XLM): 
 3e81a3f7b6e17cc22d0a1f33e9dcf90e5664b125b9e61f108b8d2f082f2d4657 

 The stolen funds were swapped into USDC and bridged off Stellar to Base via Allbridge , before moving further from Base to Ethereum via Across and Relay. 

 The bridged funds landed across Ethereum, Base, and BNB Chain in the attacker's wallet . 

 Meanwhile, ~48M XLM was frozen across the attacker's Stellar accounts by Tier 1 Validators before it could move.

 On the EVM side, three wallets received the bridged proceeds , all tagged by Etherscan.

 YieldBlox Exploiter 1: 
 0xE69f6d77DB6Ff493FDD15D8A0B390c36E18E5b21 

 Holdings: 363.98 ETH + 12.78 ETH on Base (~$729K combined).

 Notably, this wallet was funded by Binance , a major exchange hot wallet, implying either a KYC'd withdrawal or a Binance bridge conversion. Potentially traceable.

 YieldBlox Exploiter 2: 
 0x2D1CE29b4aF15fb6E76Ba9995BbE1421E8546482 

 Holdings: 357.28 ETH on Ethereum + 19.23 ETH on Base + 38,746 USDC untouched on BSC($769k).

 The wallet was funded by Allbridge Core Bridge .

 YieldBlox Exploiter 3: 
 0x0b2B16E1a9E2e9b15027AE46Fa5eC547f5ef3eC6 

 Holdings: 300 ETH on Ethereum ( $583K). A child wallet of Exploiter 2, funded directly by it.

 On February 27th, Yieldblox Exploiter 2 , moved 100 ETH to the following address: 

 0xFC51b5cD07E73020bE902A5b00902f329b083eaB 

 Which was sent to Tornado Cash: 

 0xdc082828a2358ccb33b3837b49bfe678c31259aad59c39c76916a53f8c73853b 

 On February 23 between 09:17 and 09:26 UTC, 23 transactions moved ~380 ETH from Base back to Exploiter 2 on Ethereum mainnet , using two bridge protocols simultaneously. Twelve Relay settlements at ~19.99 ETH each. Ten Across Protocol transfers ranging from 10 to 50 ETH. Consecutive blocks. Uniform batch sizing. Not scattering, consolidating . 

 This activity occurred approximately 12 hours after the Security Council sent the 72-hour white-hat bounty ultimatum . The attacker's answer was to keep moving. 

 The gas funding trail on the EVM side identifies who is behind this. Multiple wallets across both vanity address rings were funded by Etherscan-flagged phishing wallets.

 The most active gas supplier (Labeled Fake_Phishing1701177): 

 0xd7e42d9502fbd66d90750e544e05c2b3ca7cbd22 

 This address appears three times as a gas supplier across both exploit wallet rings. Three additional flagged phishing addresses complete the funding network. This is not a solo operator working from a laptop.

 The Security Council sent on-chain negotiation messages to all three EVM exploiter wallets simultaneously.

 The messages were delivered from a Coinbase-funded messenger wallet.

 Security Council Messenger: 
 0x456c2F5F3536b1D9238F4654D5242B0dF8f978AF 

 Bounty Message TX (to Exploiter 1): 

 0x7979c9faa2eba7afa29702382205930f77a461174d4eeeb3382e22bb7177171e 

 The message : “If you return 90% of the stolen funds within 72 hours, we will stop pursuing legal action. Your 3 Stellar accounts have been frozen by the Tier 1 Validators. If you contact us, we can provide instructions on how to return the 48M XLM those accounts hold on the Stellar network so it is included in the 90%.”

 The attacker's response? None . Their wallets sent back nothing. Twelve hours later, another consolidation batch ran on Relay . 

 A week of preparation, three bridge protocols, a phishing network for gas. None of that required a single vulnerability in the code. So what exactly were the auditors looking for? 

## What the Auditors Didn’t Ask

 Blend V2 wasn't unaudited. It was extensively audited. 

 In February 2025, exactly one year before the exploit, Blend V2 ran a $125,000 Code4rena competition with a Certora Formal Verification component bolted on. 

 It was a landmark event : The first Rust/Soroban formal verification contest in DeFi history.

 The contest focused on the Backstop contract , chosen for its central role in the protocol's solvency.

 Twenty-one security researchers participated . Nearly a thousand rules were written.

 A $20,000 mitigation review followed in April . 

 That's a serious security investment. 

 Here's what those credentials actually covered: Pool logic, backstop mechanics, fee vaults, auction systems, flash loan endpoints.

 The Blend V2 Audit + Certora Formal Verification's stated main invariant was precise : "Users cannot extract funds from a pool if they do not meet or exceed the minimum health factor."

 The attack ideas section directed researchers toward auctions and flash loans. The oracle, Reflector's integration, and the question of what happens when an accepted collateral asset has no functioning market, none of it was in scope.

 The Certora formal verification focused specifically on the Backstop contract's solvency . Mathematically rigorous. Provably correct. For the code that was examined. 

 The health factor check the attacker bypassed? It worked exactly as verified. It checked oracle price against liability. Oracle price was $106.74. Health factor passed. The proof held. The pool got drained. 

 It's the same architecture of failure that took down Makina Finance a month earlier - six audits certified that the contracts worked as written, and the exploit lived in the space between what was written and what the external world fed into it.

 At Makina, the gap was a permissionless AUM update function pulling spot prices from manipulable Curve pools .

 At YieldBlox, the gap was a VWAP oracle reading from a market that had effectively ceased to exist .

 In both cases, the auditors were right. The code did what it was supposed to do. Nobody asked whether the inputs were trustworthy. 

 Script3 confirmed all EURC, USDC, and XLM depositors in the affected pool will be fully compensated for losses caused by the bad debt. 

 Reflector confirmed its infrastructure was not compromised and that other assets with meaningful liquidity and multiple active traders are not at risk . The incident was isolated to the single community-managed pool, no other Blend pools were affected or vulnerable .

 QuillAudits identified the mitigations that would have prevented this : “This incident highlights the critical importance of liquidity thresholds, market depth validation, and circuit breakers when relying on on-chain DEX pricing. Even mathematically sound oracle systems can fail if underlying market conditions are economically unsound. Robust oracle design must account not just for price accuracy, but for market quality and resilience.”

 A $125,000 formal verification contest . A first-of-its-kind Rust audit. And the vulnerability was a market condition that didn't exist yet when the auditors signed off. 

 When the proof says the health factor can't be bypassed, and the attacker bypasses it by feeding the oracle a price that's 100x wrong - did the audit pass or did the threat model fail? 

 Nobody picked a lock. They just walked through a door the auditors never checked. 

 The oracle reported what the market showed. The adapter passed the price it was given. The pool handed over $10.97 million. 

 Every component performed exactly as designed, and the pool bled out anyway. That's not a bug. That's a system that was never asked whether the world feeding it data could be trusted.

 Script3 will compensate depositors. Stellar's validators froze most of the XLM before it could vanish.

 The attacker still has millions sitting in EVM wallets with a Binance KYC trail attached, and a forensic dashboard that documents every move they made. 

 The fixes are real. The accountability is partial.

 And the lesson, that a lending protocol is only as safe as the worst market it accepts as collateral, is not new. It has been written in eight figures of losses across a dozen protocols before this one.

 DeFi keeps building faster than it learns. Auditors scope contracts. Nobody scopes reality. 

 When your security model is formally verified and your protocol still gets drained by a single trade in a market with less than a dollar of daily volume, what exactly were you paying the auditors to protect? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

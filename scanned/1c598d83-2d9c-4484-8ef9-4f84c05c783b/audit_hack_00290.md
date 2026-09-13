# [H] Venus Protocol - Rekt IV exploit: On March 15, 2026, an attacker who had spent nine months quietly accumulating 84% of Venus Protocol's supply cap for the Thena token executed a Mango

## Summary
Severity: High
Target: Venus Protocol - Rekt IV
Loss: $3,700,000
Published: 3/15/2026
Source: https://rekt.news/venus-protocol-rekt4
Type: rekt-postmortem

## Details
## Venus Protocol - Rekt IV

 Wednesday, March 18, 2026 Venus Protocol - Supply Cap Manipulation 

 read this article also in : 

 Nine months of patience. One dismissed audit finding. And a protocol that had already absorbed $717,000 in bad debt from a donation-style exploit on its own ZKSync deployment twelve months earlier. 

 On March 15, 2026, an attacker who had spent nine months quietly accumulating 84% of Venus Protocol's supply cap for the Thena token executed a Mango Markets-style price manipulation attack on BNB Chain, bypassing the cap entirely through a technique called a donation attack, running a recursive borrow loop against thin liquidity, and extracting $3.7 million in borrowed assets before the position imploded into $2.15 million in bad debt . 

 Fourth major incident since 2021 . Same protocol. Same chain. The same category of collateral inflation exploit it has survived before .

 Venus's own Code4rena analysis in 2023 flagged this exact mechanism, donations bypassing supply cap logic, and the team dismissed it as ‘supported behavior with no negative side effects.

 William Li spotted it early on March 15th , flagged the attacker's address in real time, and made $15,000 shorting the collapse . 

 The attacker, despite extracting $5.07 million in assets, likely walked away with nothing, or less than nothing, on-chain .

 Venus walked away with a $2.15 million hole it will have to explain to governance.

 At some point, surviving every attack stops being a testament to protocol resilience and starts being an indictment of an ecosystem willing to keep depositing into it. 

 When the same protocol gets rekt four times in five years, each time from a variation of the same root failure, is the real vulnerability in the code, or in the decision to keep using it? 

 Credit: The Block , William Li , Venus Protocol , Blockaid , Thena , Allez Labs , Hacken , DARK HIT9 , EmberCN , ChainCatcher 
 William Li was the first to say it out loud. 

 "Hi Venus Protocol, I think there is some suspicious activity going on with your vTHE pool. Someone is 'donating' to jail-break the THE supply cap and performing a Mango-market like attack. Please pause your pool ASAP!"

 Li wasn't guessing. He had modeled this exact type of attack in a 2023 academic paper on role‑play attack strategies in DeFi.

 When THE's price started moving in ways that matched the pattern, he recognized it immediately .

 He publicly posted the attacker's address , before Venus Protocol had posted a single word. 

 Attacker address: 

 0x1A35bD28EFD46CfC46c2136f878777D69ae16231 

 Blockaid issued a community alert identifying it as "delegated borrowing abuse."

 Venus Protocol's first public statement came two hours after Li's alert : "We have identified unusual activity involving the $THE pool and are actively investigating. At this time, only the $THE and $CAKE markets appear to be affected."

 An hour later, all THE borrows and withdrawals were paused .

 Two hours after that, Venus set the Collateral Factor to zero across six additional markets - BCH, LTC, UNI, AAVE, FIL, TWT - flagged because a single wallet held more than 60% of the supplied collateral in each. lisUSD followed shortly after under the same criteria.

 Thena moved quickly to separate itself : "THENA Smart Contracts are safe. A malicious actor targeted the THE market on Venus Protocol. Your funds and positions on THENA remain SAFU." 

 By the following morning, Venus had its official account of events . The attacker spent 9 months slowly accumulating $THE to build a dominant supply position. Supply cap bypassed via direct contract transfers. Recursive loop. Bad debt created. Oracles did not fail. Venus Flux unaffected. 

 The oracle claim deserves a footnote. The official post-mortem that was released on March 17th , confirms Venus's BoundValidator actually rejected the spiking price for approximately 37 minutes before both feeds converged and it accepted the manipulated rate.

 Technically accurate, the oracle didn't fail. It resisted, then ran out of road.

 Three bullet points of damage control, and one line that buried the real story : "This is a gap in our code we are working to close."

 Make sure you read that line twice, because yes, they really said that.

 Meanwhile, Li had already closed his short position, with a profit of $15k . 

 If the researcher who modeled this exact attack class in 2023 could identify it in real time while it was still running, what was Venus's security infrastructure actually watching? 

## Nine Months in the Dark

 Most exploits are built in hours. This one was built in nine months. 

 According to Venus Protocol’s official post-mortem , starting in June 2025, a wallet received 7,447 ETH, roughly $16.29M, across 77 separate Tornado Cash transactions . 

 That ETH was deposited as collateral on Aave , used to borrow approximately $9.92M in stablecoins, and those funds were dispersed through intermediary addresses to quietly accumulate THE on the open market.

 No flags. No alerts. No rules broken. Just a patient buyer, month after month, building toward a position representing 84% of Venus's 14.5 million THE supply cap .

 Attacker Address: 

 0x1a35bd28efd46cfc46c2136f878777d69ae16231 

 Community members had flagged this address as suspicious before March 15th . Venus allegedly took no action , because technically, nothing had gone wrong yet. 

 Then the deposit flow stopped. And the direct transfers started . 

 A second attacker EOA, was also identified as part of the operation by Quill Audits , though its exact role (e.g., helper, liquidation‑front‑running, or beneficiary) is not fully detailed in the public write‑ups.

 Second Attacker Address: 

 0x43c743e316f40d4511762eedf6f6d484f67b2f82 

 Venus's supply cap is enforced in one place : The mint() function, the standard deposit path. It checks whether a new deposit would breach the cap. If it would, the transaction reverts.

 What it does not check is a raw ERC-20 transfer() sent directly to the vTHE contract. That path bypasses mint() entirely. 

 Tokens transferred this way still land in the contract . The contract's balanceOf() still counts them. The vToken exchange rate, which determines how much collateral each vTHE token represents, updates accordingly. The supply cap just never sees them. 

 The attacker's existing vTHE token count never changed. No new vTokens were minted. The same position, the same number of tokens, went from representing roughly $3.3M in collateral to over $12M , purely because the exchange rate beneath it had been inflated 3.81× by tokens the protocol never tracked.

 This is the donation attack . Transfer tokens directly to the contract, inflate the exchange rate, borrow against collateral the cap was designed to prevent you from having.

 A known vulnerability in every Compound V2 fork. Flagged in Venus's own Code4rena audit in 2023 . Dismissed by the team as "supported behavior with no negative side effects."

 The cap breach unfolded as follows : 
 12.2M THE supplied via normal deposits - 84% of cap, within limits. 

 49.5M THE - 341% of cap - via direct donation transfers. 

 53.2M THE - 367% of cap - at peak, just before liquidation. 

 Six wallets coordinated the donation transfers , pushing a combined ~36M THE directly into the vTHE contract in the opening transaction.

 Attack Contract: 

 0x737bc98f1d34e19539c074b8ad1169d5d45da619 

 The attack contract held no collateral itself, it was granted delegated permission to draw on 0x1a35's borrowing power.

 Two addresses. One position. The structure let the attacker operate the extraction separately from the collateral base that made it possible.

 With a collateral position 3.67 times the intended maximum, the attacker had what they came for : Outsized borrowing power against a token whose on-chain liquidity could barely support a fraction of the position's nominal value. 

 The loop started. 

 Deposit THE as collateral. Borrow CAKE, BNB, BTCB, USDC against it. Use the borrowed assets to buy more THE on DEX - thin liquidity, violent price impact.

 Transfer the newly acquired THE directly into vTHE, bypassing the cap again. Wait for the TWAP oracle to catch up to the manipulated price. Repeat.

 THE's spot price was pushed from roughly $0.26 to nearly $4 on the thinnest DEX liquidity available.

 Venus's Resilient Oracle, which cross‑checks prices from multiple sources including RedStone and Binance, didn't simply follow the price up. 

 The BoundValidator rejected the spiking Binance feed for approximately 37 minutes as the divergence grew too wide to accept. 

 Only when the attacker sustained enough buy pressure across multiple venues to force both feeds to converge did the BoundValidator accept the new rate.

 The oracle caught up to roughly $0.51 , not the $4 spot peak, but still nearly double the pre-attack level, and enough to justify another round of borrowing.

 The oracle had caught up. The position was loaded. What followed was the extraction.

 Attack Transaction: 0x4f477e941c12bbf32a58dc12db7bb0cb4d31d41ff25b2457e6af3c15d7f5663f 

 Second Attack Transaction: 0xce6e3eb2a28ced1ef1c2212f36736e89f647365b0dfad6c9addc4c8b31f5fb0e 

 At peak, the position held 53.2M THE as collateral against 6.67M CAKE, 2,801 BNB, 1.97K WBNB, 1.58M USDC, and 20 BTCB borrowed against it . 

 The total borrowed at peak was approximately $14.9M , the $3.7M figure widely reported represents net extracted assets after the position unwound through liquidation. 

 Around 50 exploit transactions in total, per Hacken's analysis. 

 The attack contract had also pre-supplied 1.58M USDC as collateral and borrowed 4.63M THE at 11:55 UTC , during the same opening window as the main attack. That position began liquidating at 12:04 UTC , nearly forty minutes before the primary position peaked.

 Then the attacker got greedy.

 Rather than exiting after the first extraction, they kept buying THE with borrowed funds, trying to force another leg up, another oracle update, another round of borrowing power. Sell pressure mounted. The market stopped moving. The account's health factor crept toward 1.0, the liquidation threshold. 

 When liquidation triggered, 53.2M THE hit an order book with almost no depth. The price collapsed to $0.22, below where it started. 

 The $30M in nominal collateral value that existed on paper evaporated.

 Venus was left with $2.15 million in unrecoverable bad debt : 1.18M CAKE and 1.84M THE that no liquidation proceeds could cover.

 The extracted funds remain in the attacker's wallet. No mixer activity detected as of publication. No exit path apparent on-chain. 

 Nominal collateral value and realizable liquidation value are not the same number, so why does Venus's risk framework treat them as if they are? 

## The Warning They Filed Away

 Venus didn't miss this vulnerability. They read it, considered it, and assessed it as having “no negative side effects." 

 May 2023, Code4rena's audit contest of Venus Isolated Pools documented the donation attack in detail , including a working proof of concept under finding M-10. 

 Mint vTokens, donate underlying tokens directly to the contract , watch the exchange rate inflate, borrow against collateral you were never supposed to have. The mechanics were spelled out. The math was there .

 Poorly enough that Allez Labs put it on the record in the official March 17 post-mortem, word for word : The vector "was identified in a prior Code4rena audit but was assessed as having 'no negative side effects' and was not remediated."

 Not a researcher's characterization. Not a journalist's reconstruction. Venus's own risk manager, in the formal post-mortem, confirming the dismissal happened and naming it as a root cause.

 February 2025, a donation attack hit Venus's ZKSync deployment. Not a theoretical risk, an actual exploit, using mechanics nearly identical to what just happened on BNB Chain. 

 The wUSDM exchange rate was manipulated via a direct ERC-4626 donation. Venus froze the market. The protocol absorbed $902,159 in bad debt, later offset by $163,757 in liquidation fees, leaving a net loss of $716,789 . 

 A post-mortem was published on the Venus community forum. The BNB Chain Core Pool shared the same vulnerability. Venus did not patch it.

 That's the sequence: Auditors flag the vector in 2023 , the team dismisses it. An attacker exploits the same vector in 2025 , the team absorbs the loss.

 An attacker exploits it again in 2026, on the chain that was never patched, and the team calls it "a gap in our code we are working to close." 

 Hacken flagged it explicitly in the aftermath : "Attention Compound V2 forks: Verify whether direct token transfers to your cToken contracts bypass supply-cap logic. If so, the same attack pattern may still be exploitable." 

 Venus is a Compound fork . The warning applied to them directly. It applied to them in 2023 when Code4rena raised it. It applied to them again in February 2025 when ZKSync proved the concept cost real money . 

 Hopefully, every other Compound V2 fork running the same mint() enforcement gap is now reading these same words and deciding whether to act on them or file them away.

 The community had also flagged the attacker's accumulation address before March 15th. Concentrated supply, dominant position in a low-liquidity market, wallet traceable to Tornado Cash funding . No action was taken, because every individual deposit was technically within the rules. The rules just had a gap .

 Venus's own post-incident criteria for pausing markets, market cap under $2B , 24h trading volume under $100M, DEX TVL under $40M, single-user concentration above 60%, described the THE market precisely.

 Those thresholds exist now. They did not exist as enforcement triggers before March 15th.

 Venus had the audit contest finding, the prior exploit, and the community flag, three separate signals pointing at the same gap. 

 How many warnings does a protocol need before inaction becomes a de facto policy? 

## Did He Even Win?

 Venus is sitting on $2.15 million in bad debt . The attacker may be sitting on a loss. 

 The on-chain math doesn't work out . The attacker entered with 7,447 ETH sourced through Tornado Cash and borrowed an additional $9.92 million via Aave to fund the accumulation phase. 

 Against that, they extracted roughly $5.07 million in assets from Venus - 2,172 BNB, 1.516 million CAKE, and 20 BTCB.

 The position carried roughly $30 million in nominal collateral value on paper. Liquidation turned that into nothing .

 EmberCN put it plainly : "He borrowed 9.92 million U (stablecoins) to stir things up, but the assets borrowed from Venus were only worth $5.07 million. Onchain alone, it doesn't look profitable."

 William Li, speaking to The Block, was equally blunt : "From onchain analysis, he almost didn't profit. 

 The official post-mortem goes further . Allez Labs confirmed on-chain analysis shows no net gain, then added: "The strategy could include independent wallets or CEX accounts, to long/short THE. We are coordinating with exchanges and forensic partners to pursue this line of investigation." 

 The CEX perp hypothesis isn't speculation anymore, it's the active thread Venus and its partners are pulling.

 The extracted funds remain parked in the attacker's wallet , with no clear exit path visible on-chain as of publication. No Tornado Cash activity. No bridge movements. Just sitting there.

 There is one scenario where the numbers flip. If the attacker holds large short perpetual positions on THE at a CEX , shorting into the pump, then collecting on the collapse to $0.21, the on-chain loss becomes irrelevant.

 The protocol damage was the mechanism, not the payday. THE's spot price ran from $0.26 to nearly $4, then crashed below its starting point. 

 Anyone short from the top made serious money. That position can't be verified on-chain. 

 Li himself demonstrated exactly this trade. He shorted THE on a perpetual futures contract as liquidation began and closed the position near $0.24.

 Profit : $15,000.

 Same playbook, smaller scale, fully disclosed.

 EmberCN flagged the same hypothesis: "I suspect he dominated the THE downturn through on-chain liquidations to profit from his positions on the CEX."

 Nine months of preparation, 7,447 ETH seeded through a mixer , a near-identical exploit already on the record from 2025 , and the attacker may have broken even at best, made nothing, or made their real money on a derivatives position nobody can trace. Venus absorbed the bad debt regardless of which version is true.

 Nine months of setup, an academic paper modeling the exact attack, a prior exploit on the same codebase, and Venus is left holding the bill no matter which version of the attacker's P&L is true. 

 So who actually paid the price here? 

 Four incidents in five years . One protocol that keeps surviving things that would have buried anything else. 

 $95 million in bad debt from an XVS price manipulation in 2021. 

 $14.2 million from the LUNA crash in May 2022 , as attackers exploited a stalled Chainlink oracle to borrow against artificially inflated LUNA collateral.

 $717,000 from a donation attack on Venus's own ZKSync deployment in February 2025 , a structurally related exploit on a different chain, a warning that went unheeded.

 And now $2.15 million more , left on the books after a nine-month setup that the community flagged, that an auditor documented, that a prior exploit had already demonstrated was real.

 Venus called it a gap . William Li called it a Mango Markets like-attack before Venus had issued a single statement. Hacken called it a warning to every Compound V2 fork still running the same logic. The Code4rena auditor called it in 2023 , but it was assessed as having 'no negative side effects' and was not remediated.

 Every response lands in the same place: Supply cap hardening, tighter collateral eligibility, price monitoring safeguards. 

 The same commitments that follow every incident, rebuilt on top of the rubble of the last ones. 

 This time the list is longer : A formal governance VIP for bad debt resolution, coordination with law enforcement on the Tornado Cash-sourced funding trail, and a complete re-audit of the entire core pool.

 Whether the longer list means a longer memory is the question Venus hasn't answered yet.

 ChainCatcher called Venus the “most experienced” project in the space at dealing with hacker attacks. That's one way to read it.

 Another way to frame it: 5 years of evidence that surviving an exploit is not the same as learning from one. 

 The attacker is sitting on extracted funds with no exit path visible. Venus is sitting on bad debt with a governance resolution pending . 

 The official post-mortem confirmed the bad debt will be covered by the protocol.

 They also announced as part of their short term remediation : “Reduce collateral factors for illiquid assets; introduce more conservative liquidity-weighted calibrations. All market configurations and collateral parameters, with potential delistings.”

 Venus survived again. It always does, like a defi cockroach.

 The question isn't whether Venus will survive this one. It will.

 The question is how many Compound V2 forks are reading Hacken's warning right now and deciding it doesn't apply to them, and how many of those forks will be writing the same post-mortem in six months. 

 Venus keeps surviving. Does anyone else have to get rekt before the rest of the ecosystem acts on the same warning Venus already ignored twice? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

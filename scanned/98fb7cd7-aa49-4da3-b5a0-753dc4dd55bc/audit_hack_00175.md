# [H] Moonwell exploit: A single missing multiplication , cbETH/ETH without the ETH/USD, turned a $2,200 asset into a $1.12 one, and liquidation bots didn't wait for a second

## Summary
Severity: High
Target: Moonwell
Loss: $1,780,000
Published: 2/15/2026
Source: https://rekt.news/moonwell-rekt
Type: rekt-postmortem

## Details
## Moonwell - Rekt

 Friday, February 20, 2026 Moonwell - Vibe Coding - Rekt 

 read this article also in : 

 One math error. Four minutes of chaos. $1.78 million gone . 

 A single missing multiplication , cbETH/ETH without the ETH/USD, turned a $2,200 asset into a $1.12 one, and liquidation bots didn't wait for a second opinion. They never do. 

 By the time Moonwell's risk manager slashed the borrow cap , 1,096 cbETH had already been seized for roughly the price of a parking ticket per token.

 Borrowers lost their collateral . The protocol was left with $1.78 million in bad debt .

 The root cause was buried in the GitHub commit that started it all : The commit was co-authored by Claude Opus 4.6 .

 Three oracle failures in over 4 months . Roughly $7.8 million in bad debt accumulated when all added up . 

 Same protocol, same class of error, new victims. The formula is almost elegant in its repetition - trust the price feed, skip the sanity check, watch the bots feed.

 But this time, something shifted. This wasn't just another DeFi postmortem about misconfigured oracles and insufficient testing.

 This one came with a question that the industry isn't ready to answer yet. 

 When AI writes the code and humans approve it without understanding it, who exactly signed off? 

 Credit: Moonwell , Wazz , YAM , Decrypt , Pashov , Mikko Ohtamaa , Patrick Collins , SlowMist's Cos , Irboz , WhiteHatMage 
 At 6:01 PM UTC on February 15, governance proposal MIP-X43 was executed . 

 Its purpose was routine - enabling Chainlink OEV wrapper contracts across Moonwell's core markets on Base and Optimism , a standard infrastructure upgrade to capture oracle extractable value. One configuration was wrong.

 cbETH is a liquid staking token. One cbETH buys you roughly 1.12 ETH , the extra reflecting accumulated staking rewards.

 To price it in dollars, you multiply that ratio by the ETH/USD price. It's two numbers. One multiplication.

 The deployed oracle skipped the second number entirely , treating the cbETH/ETH ratio - 1.12 - as a dollar value. An asset trading at $2,200 was suddenly reported at $1.12 . A 99.9% discount , live on-chain, open to anyone watching. 

 Liquidation bots were watching. They always are. 

 Within the same block, automated liquidators began targeting every cbETH-backed position on the protocol.

 The math was simple: Repay a dollar of debt, seize a cbETH worth $2,200 in the real world.

 Do it again. Do it a thousand times. By the time the damage was done, 1,096.317 cbETH had been stripped from borrowers - collateral wiped, positions left with residual debt they still owed, the protocol holding the bag on $1.78 million that was never coming back .

 A smaller group of users moved in the other direction , exploiting the mispricing from the supply side - depositing minimal collateral, borrowing cbETH at the artificial price , and vanishing with the spread. 

 Two attack vectors, one broken number, one transaction window before anyone could react. 

 How long did that window last? Four minutes.

 Four minutes between execution and the moment Anthias Labs detected the discrepancy and cut the borrow cap to 0.01, but by then, the bots had already done the math.

 But, the Liquidations continued, because correcting the oracle itself required a five-day governance voting and timelock period that could not be bypassed . 

 If your fastest defense moves in minutes but your attackers move in milliseconds, is four minutes a response time or a eulogy? 

## Synthetic Confidence

 Pull Request #578 landed in Moonwell's GitHub looking clean on the surface. 

 Contributor anajuliabit submitted it to activate Chainlink OEV wrappers across all remaining markets on Base and Optimism. 

 GitHub's Copilot reviewed all four changed files and generated four comments . The commit passed human review, merged, went to governance, and passed with 99.1% in favor .

 The commit message contained one line that would become the most-screenshotted text in DeFi security circles for the week : 

 Co-Authored-By: Claude Opus 4.6 

 Claude's specific contributions : Fixing int256 validation, a try/catch on chainlinkOracle() to skip re-deploying when two configs share the same oracle, removing the unused ProxyAdmin import, and swapping in assertTrue(answer > 0) to properly catch negative oracle prices. Tidy. Careful. Exactly the kind of defensive programming you'd want on a production deployment.

 What Claude did not flag: the cbETH price feed was pulling only the cbETH/ETH exchange rate and treating it as a dollar value . The ETH/USD multiplication, the one step that turns a ratio into a real price, was absent. Neither Claude nor Copilot caught it. Neither did the human reviewers. Neither did the 99.1% of governance voters who approved it .

 Tests existed. Just not the right one for this specific situation apparently. There was no price sanity check - no floor, no ceiling, no assertion that a reported price of $1.12 for an asset trading at $2,200 should halt deployment immediately.[

 Mikko Ohtamaa ran his own experiment after the fact.

 Skeptical of the "Claude wrote vulnerable code" framing, he fed the same PR directly to Claude with a precise prompt : "Inspect this pull request and changes and check what oracle address is incorrect and why, causing the ETH rate to be wrong."

 His conclusion was careful and cuts to the actual failure point : "Regardless of whether the code is written by an AI or by a human, these kinds of errors are caught in an automated integration test suite... In this case, tests existed, but there was no test case for price sanity, not in the tests, not in the production itself." He added that a human deployer should also be performing manual checks as part of the DAO process, and that none of that happened here either.

 This is where the AI blame debate gets genuinely complicated. 

 The error itself is not exotic. Senior engineers misconfigure price feeds. Auditors miss formula errors. Humans skip sanity checks under deadline pressure. 

 Every one of those failures has a human explanation that doesn't require an AI in the room.

 But AI changes the dynamic in one specific way: It is extraordinarily good at making wrong code look right. It comments cleanly. It compiles. It handles edge cases with the appearance of rigor.

 Patrick Collins of Cyfrin named it directly : "AI is really good at convincing you that your code is good. Remember, AI is like a really smart fast-working recently graduated post-grad, and is actually still kind of an idiot. And will lose you millions of dollars." 

 There is a difference between code that is correct and code that reads as correct. A human developer staring at a cbETH oracle configuration that outputs $1.12 might feel something, a flicker of wrongness, a number that doesn't match what they saw on Coinbase that morning. AI has no such flicker. It produced a plausible answer, formatted it well, and moved on. 

 Pashov, who surfaced the Claude co-authorship publicly , also provided the most honest framing after the initial storm : "Of course, human behind AI decides and reviews the code, possibly a security auditor as well. Sad to see another exploit, but makes you wonder a bit about vibe-coding ."

 SlowMist's Cos was characteristically blunt , calling it a "very low-level mistake" and followed it up with the zinger, “One highlight of this vulnerability is: Co-Authored-By: Claude Opus 4.6. Claude’s latest and strongest model.”

 Both are right. That's the uncomfortable part. The AI made the error. The humans ratified it. The governance process blessed it. And a mandatory five-day timelock made it impossible to fix once the damage had started.

 The code was wrong. Every system designed to catch wrong code said it was fine. 

 When a misconfiguration this simple survives AI review, human review, Copilot review, and a DAO vote - what exactly is the review process reviewing? 

## Forensics of a False Price

 There is no single attacker address to trace here. No exploit contract to decompile. No laundering trail to follow through Tornado Cash. 

 That's what makes this incident unusual by DeFi exploit standards, and what makes it harder to dismiss. 

 What happened on-chain was not a theft. It was a liquidation cascade operating exactly as designed, on a price that was catastrophically wrong.

 Two categories of actors extracted value. Both did so through mechanisms the protocol explicitly allows.

 The liquidation bots moved first. The moment MIP-X43 executed and the cbETH oracle flipped to $1.12 , cbETH-backed positions across the protocol crossed the liquidation threshold.

 Bots are built for exactly this moment. They scan continuously, they act in the same block, and they do not deliberate.

 Each liquidation was mechanically valid: Repay a portion of a borrower's debt, seize their cbETH collateral at the protocol's reported price, pocket the spread. At $1.12 reported versus $2,200 actual, that spread was not a margin - it was a multiplier.

 1,096.317 cbETH seized in total . Borrowers' collateral wiped. Residual debt left on the books. 

 The bad debt that remained didn't represent cbETH that liquidators failed to seize. It represents the gap between what the bots repaid and what borrowers actually owed, the unpaid loans left behind because the repaid amount was far below the actual borrowed value. 

 The over-borrowers came second, running the same mispricing in reverse. A smaller number of users exploited the distorted pricing to supply minimal collateral, massively over-borrow cbETH at the artificially low reported price, and instantly generate additional bad debt denominated in cbETH.

 The cbETH they borrowed was real. The collateral backing it was, by any honest accounting, nearly worthless. The bad debt this generated sits on Anthias Labs' public spreadsheet alongside the liquidation damage — separate mechanics, same broken number, same result.

 The full damage across eleven assets : cbETH ($1,033,393), WETH ($478,998), USDC ($232,584), EURC ($11,566), cbBTC ($11,442), cbXRP ($7,947), DAI ($1,520), USDS ($1,052), AERO ($204), MORPHO ($171), wstETH ($164).

 Total: $1,779,044.83.

 These figures represent unpaid loans - what borrowers still owed after their collateral was gone, across eleven different debt assets.

 The cbETH line is the largest at $1.03 million, but the spread across WETH, USDC, and the rest reflects the blast radius: Borrowers holding mixed portfolios had all their collateral dragged underwater when cbETH's reported value collapsed, leaving residual debt in whatever they had borrowed. 

 The receipts exist. The math is transparent. 

 There's no Tornado Cash, no self-destructing contracts, no obfuscation. The bots did nothing illegal. They followed the rules. The rules just happened to be operating on a lie.

 Governance precedent matters here. When Moonwell absorbed $1.7M in bad debt from the October 10 incident , the governance community voted overwhelmingly to use protocol reserves to cover it .

 That resolution is now the loudest thing users in the February governance forum are pointing to, because the same protocol error playbook just ran again, and the same question is back on the table. 

 When the protocol's own mechanics are the weapon and the only ones who lost were the users who trusted it, who exactly owes the debt? 

## The Roast of Moonwell

 On Twitter, the shitshow took a different shape entirely. 

 Within hours of Irboz and Pashov surfacing the Claude co-authorship , the "vibe coding" framing had escaped the security researcher niche and gone mainstream. 

 WhiteHatMage offered perhaps the most economical summary : "Moonwell forgot to add 'MAKE NO MISTAKES' to their security-whitehat agent."

 Pashov, who ignited the conversation, also tried to contain it : "First rule of using AI: make sure it is thinking critically and hallucinating as little as possible to you. Second rule of using AI: do pre-deployment rigorous audits with experienced whitehats."

 He acknowledged that the human in the loop carries the final responsibility.

 Patrick Collins dropped this banger right after : "Third rule of AI: Give it your private key if you wish to peril."

 Meanwhile yieldsandmore compiled Moonwell's full oracle incident ledger and delivered the harshest verdict : 3 incidents in just over 4 months, $7 million in bad debt, the same attacker reportedly scanning the protocol continuously between the October and November hits for extractable value.

 The conclusion was three words : "Do. Not. Use. It."

 The serial nature of Moonwell's failures is the part that cuts deepest.[

 October 10 : Oracle feeds mispriced three volatile tokens, attacker flashloaned and drained at 85-88% LTV, leading to $1.7M in bad debt . 

 November 4 : wrsETH oracle fed an absurd value - 1 wrsETH = 1,649,934 ETH - after the Balancer exploit destabilized rsETH liquidity the day before, the same attacker took advantage, $3.7M in bad debt .

 February 15 : cbETH oracle missing one multiplication, AI-assisted code, $1.78M in bad debt.

 Three incidents. The same failure mode , a price feed reporting something that should have failed any basic sanity check, executed twice with the missing ETH/USD multiplier across two different liquid staking tokens.

 The industry is building an extensive curriculum on exactly what happens when price feeds go wrong, and Moonwell has contributed three chapters. 

 When a protocol has now watched the same class of oracle error extract millions from its users three times in six months, at what point does "we're working on it" stop being a response and start being the problem? 

 Somewhere between a governance vote passing at 99.1% and $1.78 million in bad debt , the system worked exactly as designed, and that's the most unsettling part. 

 No hack. No hacker. No emergency multisig to blame. 

 Just a missing multiplication, an AI that didn't pause, a governance process that couldn't move fast enough, and a five-day timelock standing between a broken oracle and the ability to fix it.

 Three incidents in just over four months , the same class of error twice, and a protocol that declined to comment while its users filed damage reports on a governance forum.

 DeFi promised to replace trusted intermediaries with trustless code - but trustless code still has to be right, and right now nobody in the pipeline, not the AI, not the human reviewer, not the Copilot pass, not the DAO, is reliably catching wrong.

 The vibe coding debate will rage on, and Pashov and Mikko Ohtamaa are both correct: The AI made the error and the humans let it through, which means there is no single throat to choke and no single fix to ship.

 What there is, is a protocol sitting on $7 million in accumulated bad debt across roughly four months , a community of users asking to be made whole, and an industry-wide question that Moonwell just made impossible to ignore. 

 If the AI writes the code, the human approves it, the governance votes for it, and the oracle still goes live wrong, who exactly is responsible, and what are they going to do about it next time? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

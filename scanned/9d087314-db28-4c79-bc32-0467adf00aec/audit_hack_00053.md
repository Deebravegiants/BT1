# [H] Bunni exploit: Bunni thought they'd cracked the code with their custom Liquidity Distribution Function - some next-level math that would squeeze every drop of profit

## Summary
Severity: High
Target: Bunni
Loss: $8,400,000
Published: 9/1/2025
Source: https://rekt.news/bunni-rekt
Type: rekt-postmortem

## Details
## Bunni - Rekt

 Tuesday, September 9, 2025 Bunnie - Rekt - Rounding Bug 

 read this article also in : 

 One precision bug. Two pools. $8.4 million gone. 

 Bunni thought they'd cracked the code with their custom Liquidity Distribution Function - some next-level math that would squeeze every drop of profit from Uniswap V4. 

 Turned out they'd just built themselves a very expensive calculator that someone else learned to break.

 On September 1st, an attacker turned pocket change into an $8.4 million payday by exploiting Bunni's rebalancing logic across Ethereum and Unichain.

 No flash loans needed. No oracle manipulation required. 

 Just carefully sized trades that broke the math at exactly the right moments, allowing repeated withdrawals that drained pools faster than you could say "liquidity provider."

 BlockSec sounded the alarm , but by then millions were already crossing bridges to Ethereum in tidy 100 ETH chunks .

 Bunni hit the emergency pause button across all networks, but the vault was already empty. 

 When your protocol's greatest innovation becomes your fatal flaw, who's really doing the math? 

 Credit: Blocksec , Hacken , CertiK , Bunni , Victor Tran , William Li , m4rio , zeez , Cyfrin Audits , Dapp Radar 
 BlockSec fired the first shot late on September 1st , flagging suspicious transactions targeting Bunni's Ethereum contracts with losses around $2.3 million. 

 An hour later, the damage assessment exploded. CertiK identified the same exploit pattern on Unichain , pushing total losses to $8.4 million across both networks.

 Half the stolen Unichain funds had already been swapped to ETH and were bridging to Ethereum through Across Protoco l in methodical 100 ETH transfers.

 Bunni's acknowledgment came two hours after BlockSec's initial alert. 

 Their response was textbook damage control : "The Bunni app has been affected by a security exploit. As a precaution, we have paused all smart contract functions on all networks."

 About 4 hours later, Bunni had narrowed the blast radius, confirming only two pools were compromised : USDC/USDT on Ethereum and ETH/weETH on Unichain.

 Silent P from Bunni announced a pause on all contracts , while they assembled a war room with Hypernative, Cyfrin Audits, Impossible, and BlockSec.

 All hands on deck, but the horse had already bolted. 

 But how exactly do you turn a few precisely timed trades into an eight-figure heist? 

## The Math That Broke the Bank

 Bunni got rekt by their own cleverness. 

 Most DEXes stick with Uniswap's battle-tested logic. 

 Not Bunni. They cooked up their own mathematical masterpiece - a custom Liquidity Distribution Function that would milk maximum profits from every trade.

 The LDF lived to optimize liquidity distribution , with swaps triggering rebalancing when token ratios deviate significantly from targets .

 Spot a deviation and boom - time to recalculate and rebalance to keep those token ratios looking pretty. 

 Victor Tran from KyberSwap figured out what went wrong: someone discovered they could game this LDF with trades of very specific sizes. 

 These precision strikes broke the rebalancing math, causing it to spit out completely wrong calculations for how much each LP share was worth.

 The attacker just kept hitting replay - withdrawing more tokens than they should have, cycle after cycle.

 Each round made the error nastier, turning rounding mistakes into cold hard cash. 

 William Li spotted the smoking gun : the attacker had drained one balance down to a measly 25 wei. 

 When you're dividing by numbers that small, precision goes out the window and the math falls apart.

 Best part? The attacker left over 1,000 logs in their transactions , complete with helpful markers like "Depositing to euler" and "Unlock Callback."

 Basically wrote themselves a how-to guide while robbing the place. 

 When your rebalancing mechanism becomes someone else's money printer, who's watching the watchers? 

## Where’s the Money, Lebowski?

 The attacker didn't materialize out of thin air with $8.4 million. 

 Time to follow the breadcrumbs. 

 Primary Attacker on Ethereum: 
 0x0C3d8fA7762Ca5225260039ab2d3990C035B458D 

 Primary Attacker on Unichain: 

 0x0C3d8fA7762Ca5225260039ab2d3990C035B458D 

 Attack Contract on Ethereum: 

 0x657D8BcCDD9C6e1Da8DA1e7d331CFdeA8357AdBc 

 Attack Contract on Unichain: 
 0x6F559f75ba08d7f45a344E12ECBe8BC15A700DdA 

 Attack Transactions as follows… 

 Ethereum: 
 0x1c27c4d625429acfc0f97e466eda725fd09ebdc77550e529ba4cbdbc33beb97b 

 Unichain: 
 0x4776f31156501dd456664cd3c91662ac8acc78358b9d4fd79337211eb6a1d451 

 Two Ethereum wallets caught the loot: 
 0xe04efd87f410e260cf940a3bcb8bc61f33464f2b 
 0x18a0Aa63C07534f69aD626E6F72f20Cbe5969263 

 The heist played out in two acts. 

 First, $2.4 million drained from Ethereum's USDC/USDT pool. 

 Then $6 million vanished from Unichain's ETH/weETH pool - because why stop at one network when you can double down?

 Half the Unichain haul got immediately swapped to ETH and started its journey to Ethereum via Across Protocol.

 Not all at once though - the attacker was methodical, bridging funds in neat 100 ETH chunks like they were following some money laundering manual.

 By the time security firms finished tallying the damage, most of the funds were already consolidated on Ethereum, sitting pretty in those two addresses while Bunni scrambled to figure out what the hell just happened. 

 When precision errors pay better than most day jobs, who needs a resume? 

## The Audit Situation

 Here's where things get messy. 

 Who caught what when becomes a tangle of timelines and audit scope questions - the kind of complexity that makes post-mortems messy. 

 Bunni wasn't some garage operation cutting corners on security. They got themselves audited by legit firms .

 Trail of Bits (January 2025) : Caught precision issues dead-on, flagged TOB-BUNNI-13 about "lack of systematic approach to rounding and arithmetic errors" plus TOB-BUNNI-9 on excess liquidity manipulation.

 According to the advice in their audit, Trail of Bits told them to fix their rounding and add more fuzzing. Repo history shows code kept changing before, during, and after their review. 

 Pashov Audit Group (August-September 2024) : Earlier comprehensive review, found 45 issues including 6 critical ones. Code changes kept happening after they finished up.

 Cyfrin (June 2025 - Main Audit) : This is where things get complicated.

 In response to Rekt News inquiries, Cyfrin confirmed they found 50+ issues and basically said 'Considering the number of issues identified, it is statistically likely that there are more complex bugs still present... it is recommended that a follow-up audit and development of a more complex stateful fuzz test suite be undertaken prior to continuing to deploy significant monetary capital to production.' 

 Cyfrin didn't catch the specific rounding bug, but they called the bigger picture - essentially warning Bunni that more bugs were likely hiding and not to scale without additional security work.

 Cyfrin (July 2025 - Fee Override Hooklet) : Totally different scope, just covered fee stuff. Withdrawal logic wasn't even on their radar.

 Which leads us to a Move Fast and Break Things Problem. 

 Cyfrin essentially handed Bunni a roadmap to prevent getting rekt: don't scale until you've done more security work. 

 The protocol had already deployed, but the recommendation was clear - additional audits before continuing to deploy significant monetary capital.

 Bunni chose speed over security.

 TVL exploded from $2.4M to $23.9M overnight (July 31st to August 1st) following Cyfrin's audit instead of following their recommendations for additional security measures. 

 The result? An exploit by exactly the type of "complex bug" Cyfrin predicted would exist. 

 The Technical Reality (From Bunni's Own Post-Mortem ): 

 The exploit wasn't some theoretical edge case - it was a sophisticated three-step attack that Bunni's own analysis confirms could have been prevented with better testing frameworks. 

 The attack involved manipulating tiny withdrawals to exploit rounding errors, decreasing USDC active balance from 28 wei to 4 wei - an 85.7% decrease disproportionate to the liquidity shares being burnt.

 Bunni admits their existing testing framework failed: "We have Foundry unit tests and fuzz tests as well as Medusa fuzz tests, but they did not cover the scenario that occurred during the exploit".

 What actually broke? Rounding that looked fine by itself turned lethal when chained together. Cyfrin literally called this shot. 

 Post-Exploit Confirmation: 

 After getting rekt, Cyfrin dropped a detailed breakdown of exactly how the exploit worked. 

 Awkward timing, considering they'd just spent June telling Bunni that complex bugs were lurking and more security work was needed before scaling.

 The firm that predicted hidden complex vulnerabilities ended up reverse-engineering the exact complex vulnerability they warned about.

 This wasn't an audit oopsie - Bunni made a business call to ignore explicit warnings about sophisticated bugs still hiding in their code.

 Cyfrin's post-hack analysis basically confirmed their own June prediction: safe-looking code can hide nasty edge cases when operations get chained together. 

 Moral of the story: When security firms tell you complex bugs are probably still there, maybe don't YOLO into higher TVL? 

 Math is a bitch in DeFi. 

 Bunni thought they were building the future of liquidity optimization. 

 Turns out they were just building an $8.4 million lesson in why you don't mess with formulas that already work.

 Uniswap V4 gave them rock-solid infrastructure, but Bunni's custom LDF became their own weapon of mass destruction.

 The exploiter came armed with nothing but basic math and infinite patience, turning rounding errors into retirement money.

 Multiple audit firms gave their blessing, yet somehow a precision bug that any decent analyst could spot in the transaction logs sailed right past everyone.

 Bunni joins the growing pile of protocols that got too smart for their own good, proving yet again that innovation without bulletproof math is just expensive trial and error. 

 When decimals decide who gets rekt and who gets rich, why gamble on reinventing wheels that already roll? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

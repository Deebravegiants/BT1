# [M] Zero To Lend exploit: Ten months of silence can bury a lot of bad debt

## Summary
Severity: Medium
Target: Zero To Lend
Loss: $371,000
Published: 2/23/2025
Source: https://rekt.news/zero-to-lend
Type: rekt-postmortem

## Details
## Zero To Lend

 Tuesday, January 20, 2026 ZeroLend - Insolvency - Rekt 

 read this article also in : 

 Ten months of silence can bury a lot of bad debt. 

 ZeroLend's LBTC market on Base got drained on February 23rd, 2025 - just eighteen days after Ionic Money fell to the same fake collateral playbook. The protocol never said a word. 

 While users hammered Discord about frozen withdrawals, moderators reportedly blamed "high utilization" and "maintenance" - until torakapa blew the lid off in late 2025 .

 The lid that was blown off: The vault was empty, and someone forgot to mention the heist.

 A single wallet borrowed 3.92 LBTC across three transactions in 45 minutes, bridged the profits through Across Protocol, and left behind nothing but worthless PT-LBTC collateral. 

 The debt token still sits on-chain like a receipt nobody wants to acknowledge.

 GitHub commits flatlined in September . Exchange listings evaporated . The team may have ghosted their Discord and Twitter .

 $3 million in seed funding , a Twitter bio stacked with security names , and a founder who lists "over $200M+ under management" on LinkedIn - yet somehow nobody noticed when the lights went out? 

 When a protocol gets exploited and spends over ten months pretending it didn't happen, who's really running the con - the hacker who drained the vault, or the team that keeps the deposit button live? 

 Credit: torakapa , ZeroLend , QuillAudits , Halborn , Ionic Money , Lombard , DefiLlama , CoinMarketCap , OlimpiusInferno , Stack.money , OKX , Steven Enamakel (Founder of ZeroLend) 
 One tweet. That's all it took to crack carefully curated silence. 

 torakapa dropped the bomb in late 2025 : "There is no any UI issue. Zerolend are lying, they have been exploited on Feb-23-2025. The hacker supply PT-LBTC and manipulated the price to borrow 4,4421 LBTC."

 The address attached to that tweet tells a story ZeroLend likely never wanted to tell.

 The Attacker’s Address: 

 0x218C572b1Ab6065D74bEbcB708a3f523D14F7719 

 Basescan's token holdings for that wallet read like a confession. 

 ZeroLend zk Variable Debt LBTC : 3.92307607 - ZeroLend's variable debt token, proof of an unpaid loan that's been accruing interest for almost a year.

 ZeroLend PT Lombard LBTC 29MAY2025 : 10.9955337 - Pendle Principal Token, the "collateral" used to extract real LBTC from the protocol. The date in the token name marks its maturity - when PT holders can redeem for the underlying asset. Until then, it trades at a discount, making it a tempting but risky collateral choice.

 February 23rd, 2025, the attack unfolded with clockwork precision. 

 Attacker’s Address (Base): 
 0x218C572b1Ab6065D74bEbcB708a3f523D14F7719 

 Attacker’s Address (Arbitrum): 
 0x218C572b1Ab6065D74bEbcB708a3f523D14F7719 

 Attacker’s Address (Ethereum): 

 0x218C572b1Ab6065D74bEbcB708a3f523D14F7719 

 The Arbitrum and Base wallets were funded via Across Protocol bridge, PT-LBTC deposited as collateral to ZeroLend's pool, and the extraction began. 

 The attacker's wallet hit the protocol three times in 45 minutes. They "borrowed" ~3.923 LBTC (worth ~$371K now) and never paid it back. 

 Hit 1 - Borrowed 0.95324998 LBTC: 0xdf1c69feb8e63c70f874cdff22bba7c53eb42a5245e9695713e850966c54ce2a 

 Hit 2 - Borrowed 1.47687998 LBTC: 0x47fbcdc986c08bf779cb66267c3f6baa0dd43d6a8591f548dbcda5a1c9fce2d2 

 Hit 3 - Borrowed 1.492946 LBTC: 0xc02cea219b2748ccb8e28b2b23c14d7f6d3d144724ba1b9e17adbf07e70e51a3 

 All roads led to Across Protocol - the bridge that moved funds both in and out.

 The attacker arrived with 38 ETH on Base to fund the operation, swapped the borrowed LBTC through Aerodrome DEX , and left with 163.65 ETH - netting roughly $125k in profit after the round trip.

 The playbook was textbook DeFi extraction: deposit illiquid derivative as collateral, borrow liquid asset, bridge profits cross-chain, ghost the loan. Leave the protocol holding worthless paper while real money disappears. 

 That wallet still holds trace amounts - 1.5 ETH on Arbitrum , 0.5 ETH on Base . Operational dust from someone who clearly wasn't worried about covering their tracks. 

 The debt token hasn't moved. The collateral sits untouched. The loan will never be repaid.

 And for ten months, ZeroLend pretended none of it happened.

 This playbook had already claimed a much bigger victim just eighteen days earlier - and that one made headlines. 

 If Ionic Money's $8.8 million lesson was broadcast across every security feed in DeFi, how did ZeroLend miss the memo? 

## Déjà Vu in Eighteen Days

 February 4th, 2025, Ionic Money on Mode Network, $8.8 million gone, according to QuillAudits research . 

 The attack made noise across the security feed in DeFi, with the mount that was stolen being varied. Every protocol running LBTC derivatives should have been on high alert. 

 The vector was embarrassingly simple: Attackers posed as Lombard Finance team members , convinced Ionic to list a counterfeit LBTC token, minted themselves 250 fake tokens, and borrowed everything the protocol had.

 Social engineering dressed up in smart contract clothing. The attackers didn't need to find a bug - they just needed someone to pick up the phone.

 Eighteen days later, ZeroLend's Base market got hit with a variation on the same theme.

 Ionic fell on February 4th on Mode Network. 

 ZeroLend fell on February 23rd on Base. 

 Ionic's attacker used a completely fake LBTC token as collateral.

 ZeroLend's attacker used PT-LBTC, a Pendle derivative - different wrapper, same manipulation vector.

 Ionic lost approximately $8.8 million.

 ZeroLend lost around $371k.

 Ionic at least published a post-mortem . 

 ZeroLend published nothing. 

 Same asset class. Same collateral manipulation vector. Same month.

 ZeroLend wasn't some obscure fork nobody had heard of. Lombard Finance had announced them as a launch partner when LBTC went live on Base in November 2024 : "At launch, LBTC is live on Base's leading DeFi protocols, including Pendle, Aerodrome, ZeroLend and Morpho."

 Front row seats to the LBTC ecosystem meant front row seats to watch Ionic burn.

 The playbook was public. The warning signs were flashing neon. 

 Yet somehow, less than three weeks later, a nearly identical attack walked right through ZeroLend's front door. 

 Ionic at least had the decency to announce their disaster .

 They acknowledged the exploit, and let users know their funds were gone. Cold comfort, but honesty counts for something.

 ZeroLend chose a different path: silence, excuses, and a deposit button that still works today. 

 When an $8.8 million exploit becomes required reading for every Aave fork in existence, what does it say about a protocol that gets hit by the same attack eighteen days later and decides the best response is to pretend it never happened? 

## The Audit Salad

 ZeroLend's Twitter bio reads like a who's who of blockchain security: Chaos Labs, Zokyo, Halborn, PeckShield, Sherlock, Immunefi, and Cantina. 

 Impressive lineup. None of them are to blame for what happened. 

 Mundus ran a deployment check back in 2023 - verified the Aave fork had no backdoors.

 PeckShield audited the core protocol in February 2024 , before LBTC markets existed.

 Halborn's reports cover the ONEZ token contracts , not lending markets.

 Zokyo's November 2024 audit actually examined Pendle PT integration code : ATokenPendlePT.sol and related contracts. Zero critical issues. Zero high-severity findings.

 Score: 70 out of 100.

 So what went wrong? 

 The exploit wasn't a code bug. No reentrancy, no overflow, no logic flaw waiting to be found. 

 The attack walked through a risk management decision: ZeroLend chose to list PT-LBTC as borrowable collateral with oracle parameters that could be gamed.

 No audit covers "should we list this asset?" No security firm signs off on collateral factors and liquidation thresholds. That's governance. That's the team.

 Eighteen days after Ionic Money proved LBTC derivatives were being hunted, ZeroLend had PT-LBTC live as collateral on Base. The auditors didn't make that call. Someone at ZeroLend did.

 The "Audit Salad" isn't about auditors failing to catch bugs. It's about a protocol stacking logos to imply comprehensive coverage while making risk decisions no audit was ever designed to evaluate. 

 When every audit passes but the protocol still bleeds out, where does the buck actually stop? 

## The Zombie Market

 Exploits end. Zombie markets just keep feeding. 

 Ten months after the February drain, ZeroLend's Base LBTC market still accepts deposits. The "Supply" button works fine. Try to withdraw and suddenly it's "high utilization" and "please try again later." 

 Later never comes.

 One user documented the experience in November 2025: supplied LBTC, couldn't withdraw, got three different explanations from Discord - "pool is basically dry, wait for liquidity to flow back," "asset is paused for safety reasons," and "frontend/UI issue, dev team notified." They asked for one clear public status update. Still waiting.

 On-chain data reveals something uglier than a simple exploit aftermath.

 January 13th, 2026: A user deposits 0.000001 LBTC into the pool. Fourteen seconds later, that liquidity exits to a Gnosis Safe multisig wallet.

 Gnosis Safe Address: 
 0x0f2876396a71fe09a175d97f83744377be9b6363 

 Basescan shows that the wallet was created on April 27th, 2025 - two months after the February exploit. 

 Did someone see a broken pool and set up shop? 

 The wallet uses Gelato , an automated transaction relay service that lets smart contracts execute on triggers.

 Basescan's token transfer history shows this single address has executed dozens of withdrawal transactions against ZeroLend's LBTC pool over the past eight months, extracting over $100k in total. It still has funds supplied to the pool and continues siphoning whatever liquidity appears.

 This isn't trapped victims racing to escape. This is someone who built an automated extraction operation on top of a pool that ZeroLend left broken and open for business.

 Every new depositor becomes exit liquidity for an address that arrived months after the heist. 

 The APY displays tell their own story. ZeroLend's utilization mechanics follow Aave V3’s math - when almost every deposited asset has been borrowed and never returned, interest rates spike to distress levels that most users never think to check. 

 DefiLlama currently shows ZeroLend's Base deployment at around $100k in TVL.

 Meanwhile, the vital signs flatlined months ago.

 GitHub activity tracking shows zero updates since September 2025.

 Stack.money's developer metrics paint a protocol in maintenance mode at best , abandoned at worst. 

 The ZERO token tells the financial story . Down 100% from its September 2024 all-time high. 

 ZERO was delisted from OKX on June 4, 2025 .

 CoinMarketCap data shows 91% of tokens concentrated in the top ten wallets - the kind of distribution that makes exit liquidity out of everyone else.

 Twitter went quiet. Users report Discord mods offer no clarity from the dev team. The founder's LinkedIn still claims "over $200M+" under management while DefiLlama shows total TVL has collapsed to around $10 million across all chains .

 A protocol doesn't die all at once.

 It dies in stages: First the exploit nobody mentions, then the excuses that buy time, then the developers who stop committing, then the exchanges that delist, then the silence that says everything the team refuses to.

 ZeroLend hit every stage. The only thing still alive is the deposit button. 

 When a protocol leaves a broken pool open long enough for someone to build an automated extraction business on top of it, who's really running the operation? 

 Could silence be a strategy? 

 Ionic Money got hit for $8.8 million and told the world within hours. Ugly, painful, but honest. 

 Users knew where they stood.

 ZeroLend got hit for $371k and chose a different playbook - over ten months of "high utilization" excuses while the deposit button kept collecting fresh victims.

 The exploit itself was almost boring. Fake collateral, borrowed assets, bridge out, ghost the loan. A playbook so predictable it had already made headlines eighteen days earlier on a different chain.

 What wasn't boring was the aftermath. 

 No disclosure. No post-mortem. No governance proposal for reimbursement. 

 Just moderators running interference in Discord while an automated extraction operation systematically siphoned whatever liquidity appeared.

 $3 million in seed funding from firms like Momentum 6, Blockchain Founders Fund, and Morningstar Ventures.

 A founder with a University of Toronto degree and claims of managing $200 million . 

 All the ingredients of a legitimate operation, none of the accountability when things went sideways. 

 The ZERO token crashed 100% . OKX delisted ZeroLend’s token . Their GitHub went cold . The Discord turned into a shitshow. And somewhere, that deposit button still glows green .

 DeFi promised trustless finance - code as law, transparency as default, accountability baked into every block. ZeroLend delivered the opposite: A silent insolvency wrapped in audit logos and "please try again later."

 The hacker who drained the vault walked away with $371k.

 The team that let it happen? Still collecting deposits (assuming there is a team). 

 In a space that prides itself on radical transparency, what's the real cost
when protocols learn they can fail silently and face zero consequences? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

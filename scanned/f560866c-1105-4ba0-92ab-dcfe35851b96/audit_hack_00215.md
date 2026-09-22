# [C] Resolv Labs exploit: Three hundred thousand dollars walked into a protocol holding $141 million

## Summary
Severity: Critical
Target: Resolv Labs
Loss: $25,000,000
Published: 3/22/2026
Source: https://rekt.news/resolv-labs-rekt
Type: rekt-postmortem

## Details
## Resolv Labs - Rekt

 Tuesday, April 7, 2026 Resolv Labs - Private Key Leak - Supply Chain Attack 

 read this article also in : 

 Three hundred thousand dollars walked into a protocol holding $141 million. Eighty million unbacked stablecoins walked out. 

 The official post-mortem would later reveal a supply chain attack ; the breach began not inside Resolv, but at a third-party project where a contractor had previously worked. 

 A compromised GitHub credential opened a door , a malicious CI/CD workflow silently exfiltrated signing credentials, and days of quiet reconnaissance inside Resolv's cloud infrastructure ended with a single key in the wrong hands.

 That key, stored inside Resolv's cloud infrastructure , handed an attacker unlimited minting authority over Resolv Labs' USR stablecoin - no multisig required, no oracle check, no on-chain ceiling on what could be printed.

 The contract didn't malfunction. It performed exactly as designed, which is precisely the problem.

 By morning, roughly $25 million in ETH was consolidated in a single attacker wallet, and a protocol that had cleared $684 million in TVL more than a year prior , was sitting frozen, its mint and redeem functions indefinitely off.

 The collateral pool, Resolv would later insist, was never touched , a technically accurate statement that will be cold comfort to anyone who held USR at a dollar and watched it reprice to spare change. 

 When the architecture assumes the supply chain is secure, what exactly happens to everyone who trusted the architecture? 

 Credit: Chainalysis , CoinTelegraph , DefiLlama , Peckshield , Resolv Labs , YAM , Hacken , QuillAudits , Vadim , The Defiant , Omer Goldberg, 9summits , OAK Research , Morpho , Paul Frambot , Steakhouse , Lido Finance , Stani Kulechov , Samyak Jain , Inverse Finance , Gauntlet , Fluid , kooone , TheBlock , Upbit Korea , Venus Protocol , Midas , Lista DAO , BitcoinEthereumNews

 Sunday evening, and YAM was already watching the chain . 

 The alert landed first : USR was trading at one cent. Someone had just minted 50 million USR using $100k USDC.

 The transaction was sitting on Etherscan , public and unhidden, as if the attacker had no reason to hide at all.

 They didn't. The contract gave them every right to do exactly what they did.

 PeckShield picked it up roughly an hour later , flagging both the 50M mint and a second transaction, another 30M, telling the community to stay alert.

 Resolv Labs posted their first statement roughly two hours after YAM's alert : the protocol had experienced an exploit allowing attackers to mint 50 million unbacked USR, all protocol functions had been paused, and the team was actively working on recovery.

 A follow-up statement came shortly after . The collateral pool, they said, was fully intact . No underlying assets had been lost. The issue appeared isolated to USR issuance mechanics.

 Technically accurate. Operationally devastating.

 Cyvers caught the broader picture shortly after : 80 million unbacked USR printed from roughly $100K–$200K in collateral, a 500:1 mismatch between supply and backing, USR depegged to $0.257 and still falling.

 USR had already hit $0.025 on Curve, a 97% collapse , 17 minutes after the first mint transaction was confirmed.

 By the time Resolv's statement went live , the attacker had been converting for hours.

 PeckShield summarized the damage the following morning : 11,400 ETH, approximately $24 million, sitting in a single consolidation wallet. A further $1.3 million in wstUSR remained in the attacker's hands. 

 When the first security alert reaches the public before the team has assembled a quorum to respond, what does that say about the monitoring infrastructure meant to protect user funds? 

## The Key That Ran the Mint

 Resolv's USR minting wasn't permissionless. It required a privileged off-chain backend, designated SERVICE_ROLE, to finalize every swap request. 

 That design was intentional, a two-step process meant to add a layer of control between user deposits and token issuance . 

 The SERVICE_ROLE key had been held since May 2024 , controlling not just the mint function but also ExternalRequestsCoordinator and ResolvRequestsMgr , additional infrastructure contracts beyond USR issuance. One key. Multiple blast radii.

 Compromised SERVICE_ROLE EOA: 

 0x15CAd41e6BdCaDc7121ce65080489C92CF6de398 

 The official post-mortem reveals this was not a direct breach , it was a supply chain attack. 

 The attack originated at a third-party project where a Resolv contractor had previously contributed . 

 When that third-party was compromised, the attackers obtained a GitHub credential linked to the contractor's account. That credential opened a door into Resolv's code repositories .

 Once inside, the attackers deployed a malicious CI/CD workflow designed to exfiltrate sensitive infrastructure credentials without triggering outbound network traffic detection, then removed their own access to minimize their forensic footprint.

 The extracted credentials provided access to Resolv's cloud infrastructure . Over the following days, the attackers conducted reconnaissance, enumerating services and probing for API keys.

 Gaining signing authority over the minting key was not straightforward, multiple escalation attempts were denied before the attackers found a path that succeeded : Using a higher-privileged role's policy management capabilities to modify the key's access policy directly, granting themselves signing authority. 

 According to Chainalysis , the attacker used that signing authority to pass numbers the system was never supposed to see. 

 Transaction 1 - 50 Million USR minted: 0xfe37f25efd67d0a4da4afe48509b258df48757b97810b28ce4c649658dc33743 

 Transaction 2 - 30 Million USR minted: 0x41b6b9376d174165cbd54ba576c8f6675ff966f17609a7b80d27d8652db1f18f 

 The first transaction : 100,000 USDC deposited, 50,000,000 USR minted.

 The second transaction : Another 100,000 USDC deposited, another 30,000,000 USR minted.

 The contract had one job : Verify that a valid signature existed. It didn't ask whether the numbers made sense. The contract didn't blink. It was working exactly as designed .

 Hacken noted the key had controlled SERVICE_ROLE since May 2024 , nearly two years, with no multisig requirement, and no on-chain ceiling on what it could authorize .

 Vadim put it plainly : "The threat model was simply: the key won't leak. It did."

 Resolv's Governance Safe required multi-signature approval to pause the protocol. Assembling those signatures took approximately three hours, with a significant portion of that delay attributed to the multi-signature approval process.

 During that window, the exploit repeated across multiple wallets before anyone with authority to stop it had the signatures required to act. 

 When a single EOA can authorize unlimited token creation and the only circuit breaker requires a quorum no one could assemble in time, how many millions is that coordination delay worth? 

## Print, Wrap, Dump, Exit

 Eighty million USR is a lot of tokens to move without crashing yourself on the way out. 

 The attacker knew this. The exit was methodical. 

 Step One : Convert USR into wstUSR, the wrapped staked version. Rather than dumping raw USR directly into the market, which would have accelerated the depeg even further against the attacker's own position. wstUSR represents a share of the staking pool rather than a fixed number of tokens, a more fungible derivative with access to deeper liquidity.

 Step Two : Route wstUSR through DEXes including Curve, Uniswap and others, swapping into USDC and USDT.

 Step Three : Convert the stablecoins into ETH, the final destination. By the time the protocol was paused, most of the position had already cleared.

 The attacker operated across multiple wallets before consolidating: 

 Attacker EOA 1: 

 0x04A288a7789DD6Ade935361a4fB1Ec5db513caEd 

 Attacker EOA 2: 

 0xb945ec1be1f42777f3aa7d683562800b4cdd3890 

 Attacker EOA 3: 

 0x9feeeaec113e6d2dcd5ac997d5358eee41836e5f 

 Primary consolidation wallet: 

 0x8ED8cF0C1c531C1b20848E78f1CB32fa5B99b81C 

 That last address is where roughly 11,408 ETH , approximately $24.3 million, came to rest. No mixer. No bridge hop. No Tornado Cash. Just sitting there, visible to anyone with a browser, while the investigation clock runs.

 The attacker's remaining $1.2–1.3 million in wstUSR stayed in Attacker EOA 1’s wallet , a rounding error on a $25 million haul. 

 QuillAudits noted the entire operation netted an 83x return on the initial $300,000 deposit , and that the exploit cycled through three complete iterations before anyone publicly flagged it. 

 Real-time monitoring with an auto-pause capability, QuillAudits noted , could have cut losses to roughly $8 million by catching it on the first transaction.

 Chainalysis echoed the point directly : Real-time monitoring and automated response mechanisms are now a necessity, not a luxury, as exploits that unfold in minutes leave no time for reactive measures once the damage is visible.

 Resolv's infrastructure didn't catch it on the first transaction, or the second, or the third.

 The following morning, Resolv sent an on-chain message to the exploiter : Return 90%, approximately $25 million in ETH, keep 10% as settlement incentive, transfer all remaining USR under your control to the recovery address within 72 hours. Failure to comply will result in escalation and legal action. The on-chain message is visible on Etherscan .

 Standard post-exploit protocol. The attacker never responded. The funds haven't moved. 

 When the entire haul is sitting in a single wallet in plain sight and the attacker still isn't blinking, what leverage does a 72-hour deadline actually carry? 

## Friendly Fire

 The direct damage from the exploit was bad enough. 

 What followed made it worse, and it happened in two distinct phases, each more sophisticated than the last. 

 Before any curator intervened, the original on-chain impact of the exploit inside Morpho's lending markets was approximately $4,900 in USDC borrowed against USR collateral , a rounding error relative to what was about to follow. The number that actually mattered came later, once automation took over.

 Morpho operates a feature called the Public Allocator , a mechanism that allows curators to automatically route capital toward markets with high utilization , capturing better yields for depositors. Under normal conditions, it's a sensible optimization.

 On the night of March 22nd, it became an automatic credit line for anyone holding depegged USR.

 According to Omer Goldberg , multiple curators, including Gauntlet, Re7 Labs, kpk, and 9summits had all enabled automatic supply to Resolv-related markets. 

 Twenty minutes after the exploit began, at 2:41 AM UTC, Gauntlet's allocations started flowing into the broken wstUSR/USDC market , markets running on hardcoded oracles that couldn't reprice fast enough to reflect USR's collapse. 

 Wallets began invoking borrow requests immediately after each incremental allocation , draining the liquidity as fast as it arrived.

 Gauntlet's auto-supply continued for roughly 90 minutes before it was noticed and disabled. 

 Gauntlet’s first public statement acknowledged limited exposure in a few high-yield vaults while noting most Gauntlet vaults were unaffected.

 9summits, which had intervened early at 3:00 AM UTC, documented 32 attack transactions executed against its vault at 12:33 PM UTC, limiting its residual bad debt to $41,000 .

 9summits has since fully settled 100% of the stUSR in the Usual Money vault for USDC with Resolv, with depositors able to redeem their funds in the coming days.

 In total, Morpho vault curators fed approximately $6.2 million in USDC exit liquidity into broken markets after the exploit , with 96% of that flowing from Gauntlet vaults. 

 Every dollar supplied was a dollar that borrowers, exploiting the pricing gap between USR's crashed market price and its hardcoded oracle value, could borrow against worthless collateral and walk away with . 

 Omer Goldberg, founder of Chaos Labs, laid out the mechanics in a 21-post thread : The automation had no circuit breaker , the oracles were hardcoded and immutable , and their systems kept supplying liquidity into broken markets for hours after the exploit began .

 His conclusion was direct , a Public Allocator that can be triggered by anyone during a live exploit, against a hardcoded oracle, functions as an automatic subsidy for attackers.

 But the Public Allocator was only phase one. A second, more deliberate attack followed, as documented by OAK Research .

 Once curators responded by setting USR market supply caps to zero , the standard defensive move, the attacker exploited a documented vulnerability in Morpho's vault architecture . 

 By calling Morpho's supply() function with a vault's address as the beneficiary , anyone can force a vault to accumulate market shares it never chose to hold. 

 Using a flash loan to temporarily acquire a large share of the targeted vault's supply , the attacker likely force-injected USDC liquidity into the wstUSR/USDC market, then deposited their devalued wstUSR as collateral, still valued at $1 by the hardcoded oracle, borrowed the freshly available USDC, repaid the flash loan, and walked away with the difference .

 Morpho's own documentation warns explicitly that setting supply caps to zero does not prevent this class of attack. The warning, it appears, was not widely understood.

 Morpho co-founder Merlin Egalite was clear that the protocol's own contracts were unaffected and that only certain vaults had exposure. 

 Morpho Co-founder and CEO Paul Frambot confirmed roughly 15 vaults with more than $10,000 in liquidity were impacted. 

 Notably, Steakhouse , despite having been engaged as Resolv's risk manager just days prior, publishing a risk assessment that explicitly covered this class of exploit and concluded that Resolv "demonstrates institutional rigor", had no exposure to the protocol at all.

 Steakhouse later added an update to the report itself : "Unfortunately, one of the risks we highlighted in the below report materialized, leading to an exploit that allowed an attacker to mint new USR tokens."

 If your risk assessment concludes a protocol is built to handle exactly this scenario, and you have no exposure when it isn't, what exactly were you managing?

 The collateral damage extended well beyond Morpho. Across lending markets, yield products, and integrated protocols. 

 The full list of affected venues included: 

 Morpho vaults : Gauntlet USDC Core, Gauntlet USDC Frontier, Resolv USDC, 9Summits USDC, Extrafi XLend USDC, Re7 USDC, Seamless USDC, Apostro Resolv USDC, August AUSD, Clearstar Yield USDC, kpk USDC Yield, MEV Capital USDC, Keyrock USDC.

 Euler markets : Apostro Resolv, Euler Arbitrum Yield.

 Midas products : mBASIS, mAPOLLO, mEDGE, msyrupUSDp.

 Beyond those, exposure was confirmed or flagged across : yoUSD, Fluid on Arbitrum, Base, Ethereum, and Plasma, Venus Protocol Flux, Lista DAO's USD1 vault, Inverse Finance DOLA, and Upshift's coreUSDC, upUSDC, and earnAUSD products. 

 Lido Finance confirmed Lido Earn user funds were safe. 

 Aave founder Stani Kulechov stated no direct USR exposure , with Resolv actively repaying outstanding debt.

 Fluid faced over $11 million in potential bad debt from a separate hardcoded oracle , distinct from the Morpho situation, and secured short-term loans to cover losses in full.

 Inverse Finance's Risk Working Group paused the wstUSR-DOLA market within 15 minutes of the exploit ; despite $10 million in active debt, liquidations brought these position to zero, leaving residual bad debt of 340,060 DOLA. 

 Stream Finance, which had previously disclosed a $93 million loss in November 2025 , holds approximately 13.6 million RLP tokens representing roughly $17 million in pre-exploit net exposure , with outcome still uncertain as the recovery unfolds and they have been radio silent so far. Stream Finance has not tweeted since November’s disaster . 

 Euler, Venus, and Lista each took precautionary actions , pausing markets or isolating vaults.

 Cyvers VP GTM and strategy, Michael Pearl told CoinTelegraph: “That since the supply had inflated faster than the market could absorb and the token had immediately depegged, the value of the remaining tokens was significantly impaired.”

 Ledger CTO Charles Guillemet offered the measured verdict : Given USR's size, "this is not a Terra Luna-type event."

 Small comfort to the protocols still calculating their losses. 

 When a risk assessment published five days before an exploit concludes the protocol is well-designed to handle exactly this scenario , and the exploit happens anyway, what is a risk assessment actually worth? 

## Still Counting

 Resolv's official position is that no underlying collateral was lost. 

 Technically, that's true, the collateral pool backing the protocol's delta-neutral strategy sat untouched. 

 What was lost was something harder to recover: The integrity of USR's supply, the confidence of its holders, and roughly $25 million that is now sitting in an attacker's wallet.

 The protocol has been paused since the early hours of March 22nd , with the official post-mortem confirming most operations remain paused until further notice.

 Pre-exploit USR holders are being compensated on a 1:1 basis, with 98% of whitelisted redemptions already processed or in the pipeline . Work on subsequent phases covering remaining user groups is actively underway.

 Early signs of remediation are emerging, Gauntlet met with Resolv to discuss next steps and expressed confidence in a positive outcome for affected Morpho vault suppliers. 

 Fluid confirmed debt repayments have begun , with approximately $70 million in USR-related debt on BNB and Plasma chains cleared, a governance proposal published to transfer remaining debt positions to the team multisig for settlement with Resolv, and a compensation plan for all affected USR users forthcoming. 

 Venus Protocol confirmed $31.6 million in USR-related debt on Flux has been cleared , with the remaining balance expected within days and interest rates returned to normal.

 Midas confirmed mAPOLLO redeemed its USR position in full , with mBASIS and msyrupUSDp withdrawing Fluid allocations on Plasma as a precaution despite having no direct USR exposure.

 Lista DAO confirmed $8.4 million of its $8.6 million in USR-related loans has been fully repaid at 1:1 , zero loss for users and the protocol, with one position of $26,000 remaining.

 Resolv reported that over $77 million has been redeemed by allowlisted pre-exploit USR holders in the first two days , representing more than 90% of that group, with subsequent phases covering remaining user groups actively underway. 

 For anyone still trying to map their own exposure, Exposure.Forum launched during the incident specifically to track Resolv-related contagion, one screen designed to answer which curator got hit, which protocol lost how much, and whether a given vault is actually safe . 

 The RESOLV governance token fell approximately 8.5% in the 24 hours following the exploit and has continued to fall since .

 Upbit, South Korea's largest exchange, designated RESOLV as a trading caution item . 

 There is also a number sitting quietly in the background that nobody at Resolv has addressed publicly. USR's market cap fell from approximately $400 million in early February 2026 to roughly $100 million in the weeks immediately before the attack, a 75% contraction over six weeks, with no public explanation from the team.

 The SERVICE_ROLE key lived exclusively within team infrastructure .

 No evidence of insider trading has been established. 

 Resolv has engaged law enforcement and on-chain analytics firms, burned approximately 9 million of the attacker's illicitly minted tokens , and revoked the compromised SERVICE_ROLE . 

 As of March 26th, Resolv confirmed that approximately 46 million of the 80 million illicitly minted USR , roughly 57% , has been permanently removed from circulation through a combination of burns and blacklisting, with no illicitly minted assets remaining on exploiter-associated addresses.

 On April 6th, Resolv executed a smart contract upgrade to permanently burn 36.73 million wstUSR and stUSR tokens remaining in the hacker's wallets , unwrapping them to USR before sending both to the zero address, permanently beyond anyone's reach.

 The investigation is being conducted by Mandiant and ZeroShadow , with no evidence of insider involvement found at this stage. 

 The official post-mortem attributes the breach to a supply chain attack originating from a compromised third-party project where a Resolv contractor had previously contributed, not an insider. 

 The protocol's own accounting puts the collateral pool at approximately $141 million in assets, with only $0.5 million in redemptions processed before the pause, limiting the confirmed direct financial drain to the protocol itself.

 The funds haven't moved. 

 When a protocol's collateral is intact but its stablecoin crashed to two cents and its governance token is on a trading alert list, how exactly does "no underlying assets were lost" hold up as the headline? 

 February 2026 was the quietest month for crypto hacks since March 2025, $26.5 million lost, a 69.2% drop from January's $86 million , and the kind of number that lets an industry exhale. 

 Then March arrived. 

 Resolv's $25 million sits in that ledger, distinguished not by complexity but by simplicity: One key, one function, no ceiling, no check . The contracts were reviewed 18 times .

 The key had sat in that environment for nearly two years . The architecture was never a secret, it was just never treated as a threat.

 And the entry point wasn't even inside Resolv, it was a contractor's credential at a third-party project that had been compromised before the attackers ever touched Resolv's infrastructure.

 Chainalysis put it plainly : As DeFi systems become more complex and use more external services, privileged keys, and cloud infrastructure, the attack surface expands far beyond the blockchain itself.

 Eighteen audits , $500,000 bug bounty , a risk assessment published five days before the exploit .

 None of it mattered when the weakest link wasn't in the code, it wasn't even in Resolv. It was in a contractor's GitHub account at a project they'd worked on months before. 

 If the industry already knows that off-chain infrastructure and their teams are the new front line, why does it keep treating it like an afterthought? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

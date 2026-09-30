# [C] Nesa exploit: A quarter of Nesa's token supply arrived on Ethereum in a single transaction

## Summary
Severity: Critical
Target: Nesa
Loss: $50,000,000
Published: 8/24/2026
Source: https://rekt.news/nesa-rekt
Type: rekt-postmortem

## Details
## Nesa - Rekt

 Friday, September 11, 2026 Nesa - Cosmos - Rekt 

 read this article also in : 

 A quarter of Nesa's token supply arrived on Ethereum in a single transaction. 

 Explaining it is still not finished. 

 On Aug. 24, an attacker used the same Cosmos EVM vulnerability chain that had already hit MANTRA, TAC, and KiiChain to withdraw 257,703,733 NES from Nesa through Hyperlane to Ethereum, about 25.8% of the token's stated supply .

 Bubblemaps estimated that the bridged position was worth roughly $50 million.

 With NES trading near $0.20 in the days before the exploit. CoinGecko’s historical data places the withdrawal in the roughly $50 million-to-$53 million range at prevailing pre-crash prices.

 Nesa became the fourth publicly identified chain in the wave , five days after Cosmos EVM shipped state-breaking patches described only as containing "important security fixes." 

 Nesa said only that it had "identified malicious behavior" and would restore services after applying a fix and further safeguards. 

 A statement that vague explains nothing by itself. So who ended up doing the explaining instead? 

 Credit: Cosmos Labs , Rarma , Bubblemaps , CoinGecko , Grey Ledger , Nesa , MANTRA , KiiChain , TAC , bitvavo , Binance Wallet

 Nesa's own statement arrived first , and said almost nothing. 

 Early on Aug. 24, the team wrote that it had identified malicious activity exploiting a Cosmos EVM vulnerability , that it was taking action to limit the impact, and that services would return after a software fix and further remedies. It said exchanges had been notified. It named no mechanism, no attacker wallet, no affected account, no loss figure.

 Nesa's public endpoints returned 503 errors in the hours after that notice . With no working explorer or RPC endpoint, outsiders could not inspect the source-chain transactions, contract calls, balances, or state changes behind the withdrawal.

 As of September 8, its public explorer still returned no usable block data and reported 0% overall and block uptime .

 Without a working explorer or publicly accessible RPC endpoint, outsiders could not inspect the source-chain transactions, contract calls, balances, or state changes behind the withdrawal. 

 What remained available was Ethereum. Nesa’s own miner-rewards tool configured Hyperlane Nexus as its default NES bridge , and Hyperlane’s official registry assigns Nesa domain 41443 . 

 The Ethereum-side Hyperlane delivery shows 257,703,733.288579599652028616 NES arriving from Nesa to an attacker-controlled Ethereum address.

 Rarma reconstructed the observable bridge flow from those records : An attacker acquired and deposited 1,114,564.66 NES into Nesa between 03:13 and 04:12 UTC, then received 257,703,733 NES through a Hyperlane withdrawal on Ethereum.

 The difference is approximately 256.6 million NES . That gap doesn't by itself identify the exact call made on Nesa's side or prove the precise theft mechanism.

 What it shows is the scale of an unexplained bridge imbalance: An observable withdrawal more than 230 times the attacker's own deposit, visible on Ethereum before Nesa attached a single figure to anything.

 Rarma flagged the limit of his own reconstruction . With Nesa's nodes down, he couldn't confirm which Cosmos EVM precompile the attacker had actually used.

 The link to the same vulnerability chain that had already hit MANTRA, TAC and KiiChain was a pattern: Same ecosystem, same week, same bridge-out shape.

 Cosmos Labs' Aug. 28 postmortem would later confirm six networks were exploited using that shared vulnerability chain , but it named only MANTRA, TAC and KiiChain outright. Nesa was not included in that count. 

 If three chains can point to the exact call that drained them and a fourth can't, is that a difference in what happened, or a difference in who bothered to say? 

## Confirmed Elsewhere

 The bug was not new by the time it reached Nesa. 

 On May 13, Cosmos Labs opened a pull request titled “fix: harden statedb balance and event amount handling.” Its description said the change would “guard StateDB balance subtraction against underflow” and make precompile balance-event parsing denomination-aware. The fix was merged to cosmos/evm’s main branch two days later. 

 The proof of concept used a six-decimal network. Cosmos Labs says it attempted to reproduce the issue on 18-decimal configurations and failed , then incorrectly concluded that the flaw did not put live funds at risk, even though all known production Cosmos EVM networks used 18 decimals.

 Cosmos Labs says that assessment led it to use a public "silent patch" process . A fix was merged to cosmos/evm's main branch on May 15 .

 When a patch is public, what exactly is silent about it?

 The mechanism is two balance-accounting bugs chained together . A vesting account can delegate locked coins through the EVM staking precompile, even when those coins are not spendable in Cosmos EVM's balance view. 

 But Cosmos EVM's StateDB tracks only the spendable balance . Delegate more than that spendable portion and the post-delegation write-back underflows, wrapping the EVM-visible balance to roughly 2^256. 

 The attacker can then use that artificial balance against a high-balance victim account , such as the zero address or a multisignature wallet created at chain genesis.

 Sending 2^256 minus the victim's balance to that account overflows its balance to zero . The attacker ends up holding the victim's original balance.

 By deploying a malicious contract at a deterministic address first turned into a vesting account , the attacker could trigger the underflow and the victim-balance overflow within one transaction.

 The net change in source-chain supply was zero : No new tokens were created; real balances were reassigned. 

 On Aug. 19, Cosmos Labs backported the fix to the v0.6.x and v0.7.x release branches , saying in its later postmortem that it obscured the patch to reduce the risk of attackers identifying the vulnerability. 

 The patches shipped later that day as v0.6.2 and v0.7.2 , described only as containing “important security fixes.” The release notes did not identify the vulnerability, assign a CVE, or describe a risk to live user funds.

 MANTRA was exploited the next day.

 TAC and KiiChain followed two days later.

 Cosmos Labs’ timeline documents the MANTRA, TAC, and KiiChain incidents with exploit transactions , block heights, and bridge movements. 

 On KiiChain, it identifies an exploit transaction and says approximately 148.3 million KII was withdrawn through 18 distinct exploit iterations. 

 Nesa never supplied the equivalent account. No public technical postmortem has identified a Nesa-side CreateVestingAccount transaction, the staking-precompile call, or the victim account whose balance was reduced.

 Cosmos Labs said six networks were exploited through the same vulnerability chain , but provided detailed timeline entries only for MANTRA, TAC and KiiChain; it said it was omitting the other three "for brevity." 

 Nesa's own incident announcement and the Ethereum-side bridge evidence make it a suspect member of that unnamed group, but Cosmos Labs did not identify it by name or provide a Nesa-specific transaction account. 

 If three chains can point to the exact call that drained them and a fourth cannot, is that a difference in what happened, or a difference in who chose to say? 

## The Discount

 The number that mattered to headlines was never the number that mattered to the attacker. 

 A Hyperlane transaction minted 257,703,733 NES on Ethereum to the bridged-NES recipient wallet on Ethereum , the same wallet Rarma identified as the attacker’s primary Ethereum address . 

 Bubblemaps characterized the position as roughly $50 million in NES bridged back to Ethereum.

 Turning that position into money meant selling into a market that was collapsing as the attacker tried to exit.

 NES closed Aug. 24 at $0.01347432 , down from $0.195893 the day before.

 At 13:40 UTC, the bridged-NES recipient wallet on Ethereum burned 25,000,000 NES .

 The Nesa-directed message was not delivered before the chain stopped. If Nesa restarted without rolling back past the message, Rarma said a later Hyperlane delivery could mint the 25 million NES unless Hyperlane blocked it . 

 The rest went to the market. Rarma traced sales between 15:11 and 16:09 UTC from a separate wallet , which he identified as funded by the attacker's primary address. 

 He counted 185,744,335 NES sold across 241 fills through CoW Protocol and Uniswap V4 . The realized price fell from $0.0125 to $0.00032 as the sales progressed.

 Rarma calculated proceeds of 95.97 ETH, about $237,208 at the time.

 The reported 185,744,335 NES in sales on CoW Protocol and Uniswap V4 and the 25 million-NES burn account for roughly 210.7 million NES of the 257.7 million withdrawn , leaving about 47 million NES outside those two reported flows. 

 Where that remainder went is not publicly clear, since Nesa’s blockchain is offline as of publishing, limiting independent review of the Nesa chain-side record. 

 Bridge Withdrawal on Ethereum (257,703,733 NES): 0xd443eabd4cfa1be6ad5f7ef861db9a9f271305040615667ed336bc195af05080 

 Bridged-NES recipient Wallet on Ethereum: 0x9AE755D23Fc948fE94C9364A2398fd508a2AB0d2 

 Nesa-Directed Bridge Attempt on Ethereum(25,000,000 NES Burn): 0x575d6cc254ed1e9313bbb0fdc93c1bda937993dbe8b9b7db8a85911166c2e26d 

 Exit-Trading Wallet on Ethereum: 
 0xB92dF70F3d25eD25265c7C341C9D2550c42Ff83A 

 Bubblemaps later estimated that the attacker spent roughly $255,000 on the operation and sold for about $315,000 , netting approximately $60,000 in profit.

 It also reported tracing the attacker's operational funding to Monero and described the tokens moving through a network of wallets before being swapped into ETH and deposited to centralized exchanges.

 That estimate reflects Bubblemaps' own wallet-attribution and cost-basis assumptions , not a confirmed final payout.

 A quarter of a token's supply crossed a bridge in one transaction.

 What survived the exit was not the price quoted before the theft, but whatever liquidity was left once the market had already priced in the damage. 

 What does a nominal theft figure measure when it represents neither the attacker's proceeds nor the value the market could actually absorb? 

## Still Waiting

 The three chains Cosmos Labs named in its timeline did not respond alike, but each publicly said more than simply that it had halted. 

 MANTRA published a technical postmortem on Aug. 28 , eight days after its Aug. 20 halt . 

 It identified the Cosmos EVM exploit path , put the drain at 720.9 million MANTRA, roughly $3.6 million at its stated pre-incident price , and identified the affected accounts as a burn address and a dormant genesis-era multisignature wallet .

 KiiChain published their own Technical Post-Mortem the day after their Aug. 22 exploit . It named the exploit mechanism, the attacker’s infrastructure, and 18 distinct exploit iterations, separating the loss between funds immobilized on KiiChain and funds that reached the BNB Chain.

 Its report argued that the loss was avoidable , citing Cosmos Labs’ disclosure process and the absence of an earlier halt recommendation.

 TAC initially said it would defer its postmortem and relaunch plan after saying Cosmos Labs had asked it to wait, while affected networks were patched. 

 On Sept. 2 TAC finally followed through, a s they published a technical postmortem and recovery plan , identifying the drained staking pool, the exploit transaction, the attacker’s bridge-and-sale path, and a proposed recovery process. 

 Nesa never set a public deadline for a technical account or restart. Its Aug. 24 statement said services would return “after applying a software fix and further remedies.” 

 No restart date followed. No loss figure, no attacker wallet, no transaction account, no technical explanation of the path through which balances were taken.

 A follow-up on Sept. 5 called the incident a "pre-meditated set of operations" exploiting "a widely used attack vector” , said the chain had been "fully patched with direct support from the official upstream code maintainers," and said exchanges would reopen deposits and trading "this week." It still gave no mechanism, no figure, and no wallet. 

 A day later, Nesa announced new canonical NES contract addresses on Ethereum and BSC as the token migration moved forward. 

 Binance Alpha laid out its own arrangement on Sept. 9 : A 1:1 contract swap for NES held before deposits closed on Aug. 24 at 14:51 UTC, separate refunds for anyone who net-bought during the halt window, and a trading resumption set for Sept. 10.

 An exchange again supplied the operational specifics , the exact timestamps and the eligibility rules, that Nesa's own statements had not.

 Exchange communication arrived faster. On Aug. 24, bitvavo paused NES deposits and withdrawals , saying a “critical consensus vulnerability” had been exploited, causing vulnerable nodes to accept invalid blocks. 

 That was not a technical postmortem , but it gave customers a more specific description of the operational issue than Nesa had publicly supplied. 

 Cosmos Labs’ Aug. 28 postmortem confirmed six exploited networks , but recorded transaction-level timelines only for MANTRA, TAC, and KiiChain, saying the details of three others were omitted “for brevity.” 

 Nesa’s incident statement and the Ethereum bridge record are consistent with its being one of those unnamed networks , but Cosmos Labs did not identify it by name. 

 What does it mean when, two follow-up statements later, a chain's account of a quarter-supply bridge-out still hasn't gone beyond containment language? 

 A single transaction bought Nesa silence , not resolution. 

 Nesa said it had “identified malicious behavior” , but its public explanation did not substantially extend beyond that containment notice. The detailed transaction trail came from Ethereum. 

 The possible root-cause account came from Cosmos Labs’ ecosystem-wide postmortem , which confirmed six affected networks but did not identify Nesa or provide a Nesa-specific transaction account.

 MANTRA, KiiChain, and TAC eventually published their own accounts.

 Cosmos Labs confirmed six affected networks , but provided detailed timeline entries only for those three, saying it omitted the other three “for brevity.”

 Nesa’s announcement and Ethereum bridge record are consistent with it being one of those unnamed networks, not proof that Cosmos Labs counted it among them.

 A quarter of Nesa’s stated supply crossed a bridge in one transaction . 

 What does a Cosmos EVM chain owe token holders when the fullest public account of its loss comes from everyone but the chain itself? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

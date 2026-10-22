# [C] KelpDao exploit: On April 18, 2026, an attacker fed false data to the single verifier standing between LayerZero's cross-chain bridge and 116,500 rsETH in user deposit

## Summary
Severity: Critical
Target: KelpDao
Loss: $290,000,000
Published: 4/18/2026
Source: https://rekt.news/kelpdao-rekt
Type: rekt-postmortem

## Details
## KelpDao - Rekt

 Friday, April 24, 2026 KelpDAO - LayerZero - Aave 

 read this article also in : 

 Nobody hacked KelpDAO. They hacked what KelpDAO trusted. 

 On April 18, 2026, an attacker fed false data to the single verifier standing between LayerZero's cross-chain bridge and 116,500 rsETH in user deposits , roughly 18% of the token's entire circulating supply . 

 Approximately $290 million gone .

 The contract saw a valid signature. It did what valid signatures tell it to do. It released the funds.

 What followed wasn't just a theft. It was a controlled detonation inside DeFi's most trusted lending infrastructure.

 The stolen rsETH went straight into Aave as collateral , borrowed real WETH against itself, and was gone before the protocol's emergency multisig had assembled enough signatures to hit pause.

 Aave's TVL shed $6.28 billion in under 48 hours . 

 WETH pools hit 100% utilization, trapping depositors who hadn't moved fast enough. 

 Nine protocols froze markets.

 Arbitrum's Security Council used emergency powers to seize 30,766 ETH from the attacker's wallet on-chain , a move that drew as much debate as the exploit itself.

 LayerZero blamed KelpDAO's single-verifier configuration . 

 KelpDAO said that configuration was LayerZero's own documented default . 

 Security researchers pointed out that LayerZero still hasn't explained how an attacker got root-level access to their RPC nodes in the first place.

 North Korea's Lazarus Group is the preliminary attribution . That makes this the second nine-figure DeFi theft in eighteen days, both linked to the same state-sponsored operation, more than $577 million extracted inside three weeks .

 Every audit came back clean. Every on-chain check passed. The verification layer failed , and that layer wasn't in any audit scope. 

 When the most dangerous attack surface in DeFi is the off-chain infrastructure nobody reviews, and the verification layer sits outside every audit scope, what exactly is the industry's plan for the next one? 

 Credit: TheBlock , The Defiant , The Daily HODL , Arbitrum , CoinDesk , Prince , BleepingComputer , QuillAudits , Vladimir S. , PeckShield , Cyvers , KelpDAO , Aave , Marc Zeller , DK27ss , Banteg , LayerZero , defiprime , Pablo Sabbatella , Griff Green , wallisi , CoinTelegraph , tanuki42 , Elliptic , Chainalysis , TRM Labs , Blockworks , Omer Goldberg , The Daily HODL , Monetsupply , Carlos , Andy , Lido , Paul Frambot , Fishy Catfish , Ethena , EtherFi , Curve , WBTC , TRON , Beau , MOCA Foundation , ApeChain , Morpho , Solv Protocol , Brale , AlphaFolio , Coin Insider , Mantle , witcheer , Dune , Bartek.eth , Stani Kulechov , BanklessTimes 
 Vladimir S. was the first on the scene. 

 After the drain transaction cleared, he was already posting : "KELPDAO'S liquid staking token potentially exploited for over $100M!"

 The $100M figure was wrong. But Vladimir didn't know that yet. Nobody did. The attack had finished before most of the industry had finished, and the on-chain picture was still resolving in real time.

 PeckShield followed 36 minutes later , a terse public nudge directly at KelpDAO's account and a single Etherscan link. No estimate. Just the transaction.

 Attack Transaction: 
 0x1ae232da212c45f35c1525f851e4c41d529bf18af862d9ce9fd40bf709db4222 

 ZachXBT landed on Telegram shortly after - wallets identified, Tornado Cash funding confirmed, the number already revised upward. 

 His post named six attacker addresses and put the figure at $280M+ : "KelpDAO appears to have had $280M+ stolen one hour ago on Ethereum and Arbitrum. The attack addresses were funded via Tornado Cash." 

 Then came the firms, in close succession. CertiK confirmed ~$290M transferred and traced the bulk of it to two addresses.

 Cyvers put a sharper number on it : $293.7M drained from the rsETH Adapter, already split across chains - $178M on Ethereum, $72M on Arbitrum - and the attacker's Tornado Cash trail mapped through intermediate wallets.

 ZachXBT had already named six attacker addresses on Telegram; Cyvers and CertiK confirmed the primary ones publicly within a couple hours.

 Attacker Addresses: 
 0x8B1b6c9A6DB1304000412dd21Ae6A70a82d60D3b 
 0x5d3919F12bCc35c26Eee5F8226A9bee90c257Ccc 
 0xCBb24A6B4DAfaAA1a759A2F413eA0eB6AE1455CC 

 KelpDAO's official response came an hour and a half after Vladimir S. made the explicit known to the world . Not a post-mortem. Not a number. Just confirmation that something had happened and a list of partners they were now calling . 

 "Earlier today we identified suspicious cross-chain activity involving rsETH. We have paused rsETH contracts across mainnet and several L2s while we investigate. We are working with LayerZero, Unichain, our auditors and top security experts on RCA." 

 By the time that statement went live, the WETH was already gone . Aave was already accumulating bad debt .

 The drain had been done for 46 minutes and the only thing KelpDAO's multisig had managed to do in that window was hit pause , after the vault was empty.

 Marc Zeller didn't wait for an official update. He posted his own warning to Aave depositors in real time : "If you have WETH on Aave V3 Core, withdraw now, ask questions later."

 By the time KelpDAO confirmed anything, the rsETH was already posted as collateral on Aave , the WETH was already borrowed out , and the damage was already done. 

 When the weapon is the collateral and the exit is someone else's liquidity pool, what exactly does a pause button protect? 

## One Verifier, One Point of Failure, One Transaction.

 Understanding what broke requires understanding what KelpDAO actually built. 

 rsETH is KelpDAO's liquid restaking token. Users deposit ETH, the protocol routes it through EigenLayer, and users receive rsETH as a tradeable receipt that earns restaking yield. 

 By April 2026, rsETH had been deployed across more than 20 networks - Arbitrum, Base, Mantle, Linea, Unichain and others - all of them connected back to a single custody pool sitting on Ethereum mainnet via LayerZero's OFT bridge standard.

 That custody pool is the key detail . When users bridge rsETH from Ethereum to another chain, their tokens are locked in an adapter contract on Ethereum .

 A corresponding amount is minted on the destination. When they bridge back, the destination burns, and Ethereum releases from the shared pool.

 That shared pool was holding around 116,723 rsETH when the attack hit. It was left with 223 after . 

 LayerZero V2 relies on Decentralized Verifier Networks - DVNs - to confirm that cross-chain messages are legitimate before funds move. 

 Each DVN independently observes the source chain , verifies the transaction happened, and commits a signed attestation to the destination. Once the required number of DVNs have signed off, delivery is authorized .

 The operative word is "required number." LayerZero's architecture allows, and explicitly recommends, running multiple independent DVNs , requiring consensus across verifiers before any transfer is authorized .

 The on-chain configuration for KelpDAO's Unichain → Ethereum path read as follows : 

 KelpDAO OApp Config: Unichain → Ethereum
 requiredDVNCount: 1
 optionalDVNCount: 0
 optionalDVNThreshold: 0
 requiredDVNs: [ 0x589dedbd617e0cbcb916a9223f4d1300c294236b ]

 One required DVN. No optional DVNs. Zero threshold.

 The sole authorized verifier was LayerZero Labs' own infrastructure, labeled "LayerZero: DVN" on Etherscan. One compromised signature was all it would ever take. 

 The attacker knew this. What they needed to do was make that one DVN sign something that never happened. 

 LayerZero's post-mortem describes the method as RPC poisoning , though researchers have pushed back on that framing.

 Banteg put it more precisely : This was not poisoning from outside the trust boundary, it was a perimeter breach. The attackers got inside LayerZero's trust boundary, accessed the RPC list, compromised two nodes the DVN depended on, and swapped the op-geth binaries. A targeted implant operating inside the trust boundary - not a network-shaped attack, a supply-chain-shaped one.

 LayerZero's own post-mortem adds that the attackers then DDoS'd the remaining clean RPC nodes to force full failover onto the poisoned infrastructure.

 A node Banteg's post-incident analysis identified as operated by QuickNode . 

 The malicious RPC nodes were surgical. They served forged data exclusively to the DVN's IP addresses - telling it a transaction had occurred on Unichain - while returning honest responses to every other caller, including LayerZero's own monitoring. 

 When the attack was done, the binaries self-deleted , wiping logs, configs, and any forensic trace.

 The attacker's total seed capital for the entire operation : Approximately $230 in ETH from Tornado Cash, received roughly ten hours before the drain. 

 Funding Transaction: 

 0xcb2ee450d6e770216dc3061750b4ac5b5fa494666bcf7eaa936411733e2ef7ee 

 With the DVN reading fabricated chain state, the attacker submitted a forged packet claiming 116,500 rsETH had been locked and burned on Unichain. 

 The DVN's 2-of-3 internal multisig signed off. The packet was certified valid .

 Ethereum's endpoint did its only check - hash equality - which passed , because the hash matched the signed payload. The adapter released the funds.

 Forged Packet: Nonce 308 
 Recipient: 0x8B1b6c9A6DB1304000412dd21Ae6A70a82d60D3b 
 Amount: 0x1b1ff0ed00 - 116,500 rsETH
 Gas: 94,456
 GUID: 0x3f4510d855cf3a805fec59daafae640d290749b7bf1e5450f91b5fb0018b3b4e

 The proof that it was forged is written on-chain in three places. 

 Unichain's outbound nonce never advanced past 307 , nonce 308 never existed on the source side. 

 Unichain's rsETH total supply at the time was 49.26 rsETH , physically impossible to burn 116,500.

 No Transfer event , no burn to the zero address, no PacketSent event appeared on Unichain for the relevant block window.

 The control case is nonce 307 , a legitimate transfer of 0.006 rsETH two days earlier , which shows exactly what a real bridge transaction looks like: a burn on Unichain, a release on

 Ethereum, nonces advancing cleanly on both ends. 

 Nonce Mismatch - On-Chain Proof as follows… 

 Unichain outboundNonce 307: Source never sent nonce 308
 Ethereum inboundNonce 308: Accepted a packet that never existed
 Unichain rsETH supply 49.26 rsETH: Impossible to burn 116,500

 The attacker had also queued a second packet . 

 Nonce 309 , same structure, targeting another 40,000 rsETH , roughly $100 million. 

 Two delivery attempts were made and both reverted .

 KelpDAO's emergency multisig had just enough time to freeze the recipient address .

 The second packet's payload hash is still sitting committed on Ethereum's endpoint, undeliverable . 

 Whether LayerZero's account of how their RPC nodes were breached is complete is a separate question. 

 The entry point, how the attacker gained root-level access to replace binaries on independent infrastructure clusters, has not been publicly explained.

 What is not in dispute is the structural condition that made any of it possible.

 No reentrancy. No integer overflow. No signature replay. No flash loan. A pure verification-path failure, enabled by a configuration decision, executed against infrastructure that LayerZero has still not fully accounted for.

 LayerZero says it communicated best practices around DVN diversification to KelpDAO , who chose to maintain the 1-of-1 setup regardless. KelpDAO says it was LayerZero's documented default , affirmatively confirmed as appropriate. 

 Both statements can be true, so whose infrastructure was it that got breached? 

## Following the Money

 The attacker didn't try to sell 116,500 rsETH into the open market . That would have crashed the price inside the first block and capped the extraction at whatever DEX liquidity could absorb. 

 They had a better idea, and they'd clearly planned it in advance. 

 Within minutes of the drain, the stolen rsETH was distributed across eight pre-staged cash-out wallets .

 Each one followed the same sequence: Deposit rsETH into Aave V3 as collateral , set eMode to 3 , borrow ETH at roughly 99% effective LTV , then forward everything to a central collector address .

 By 27 minutes after the initial drain, the Ethereum collector already held 75,700 ETH from five branches alone .

 The largest single branch was wallet 0x1F4C1c2e610f089D6914c4448E6F21Cb0db3adeF , which received 53,000 rsETH and immediately opened a position on Aave V3 . 

 It pulled ETH in four sequential draws over three minutes , then forwarded the full balance to the collector. 

 Branch Wallet - Aave V3 Ethereum 

 Wallet: 0x1F4C1c2e610f089D6914c4448E6F21Cb0db3adeF 
 rsETH supplied: 53,000
 WETH borrowed: ~52,440 ETH
 Position status: Still open

 That position is still open . The borrowed WETH was forwarded. The rsETH collateral remains in Aave, worthless as backing, unliquidatable at any meaningful price. It's Aave's problem now.

 Across all branches , the attacker supplied 89,567 rsETH to Aave and walked away with 82,650 WETH and 821 wstETH.

 Smaller amounts were also deposited on Compound V3 and Euler , yielding approximately $39.4 million and $840,000 in additional borrows respectively, before those markets were frozen. 

 Aave Positions - Total Across All Branches 

 rsETH supplied: 89,567 ( $221M)
 WETH borrowed: 82,650 ( $190M)
 wstETH borrowed: 821 (~$2.3M)
 Collector address: 0x5d3919F12bCc35c26Eee5F8226A9bee90c257Ccc 

 The extraction split geographically almost immediately . Around $178M consolidated on Ethereum mainnet. Around $72M landed on Arbitrum. 

 Arbitrum was where the first containment win happened. 

 On April 20, Arbitrum's 12-member Security Council took emergency action , using a privileged system-level transaction to forcibly move 30,766 ETH from the attacker's Arbitrum address into an intermediary frozen wallet, bypassing the attacker's controls entirely.

 The Council moved first. Nine of twelve members voted in favor . 

 The freeze was completed at 11:26 PM ET . 

 Arbitrum Freeze: April 20, 2026 

 ETH frozen - 30,765 : ~$73.6M
 Frozen wallet: 0x0000000000000000000000000000000000000DA0 
 Release condition: Arbitrum governance vote required 

 The Arbitrum move was effective. It was also controversial.

 Multiple voices in the ecosystem pushed back on a council having the authority to unilaterally freeze funds by decree , arguing it undermined any meaningful claim to decentralization.

 Griff Green, a council member, stated publicly that the decision was not made lightly : "Countless hours of debates, technical, practical, ethical and political".

 Marc Zeller put it more bluntly : "Every cell of my being is meant to be against what Arbitrum just did. Yet I understand their decision. People getting their money back matters more than convictions that would allow unc Kim to walk away with a payday." 

 With the Arbitrum position locked, the attacker accelerated activity on Ethereum mainnet. 

 75,701 ETH - approximately $175M - began routing out through a combination of THORChain, Umbra, Chainflip, and BitTorrent chain . The destination, in each case, was Bitcoin.

 THORChain enables direct chain-to-chain swaps without custodians or KYC. Umbra is a stealth address protocol. Neither requires identity verification.

 Laundering Routes (Post-Arbitrum Freeze) 

 Primary: THORChain ETH → BTC
 Secondary: Umbra (~$78K), Chainflip, BitTorrent chain

 ETH moved: ~75,701 ETH - ~$175M

 This is the same exit playbook used in the Bybit hack of 2025, where roughly 83% of stolen ETH was converted to Bitcoin , with 72% moving through THORChain alone. 

 On-chain analysis from tanuki42 noted the KelpDAO proceeds were already commingling with funds from other TraderTraitor operations , including the 2025 BTCTurk hack and Bybit, suggesting the same third-party laundering teams are being deployed across operations. 

 Less than 0.768 ETH remained in the original exploiter address by the time investigators had fully mapped the exits. The wallet that received 116,500 rsETH had been nearly completely cleared .

 This is what a state-sponsored cashout looks like when it goes well for the attacker - partial freeze, full laundering, and a governance debate about decentralization as the exit. 

 If the only thing that stopped more of it from leaving was a 12-member governance body acting in hours, what does that say about the actual recovery options available when a state-sponsored actor decides to cash out? 

## The Usual Suspects

 Attribution in crypto exploits is rarely clean. This one moved faster than most. 

 LayerZero's Incident Statement , published April 19, named North Korea's Lazarus Group, specifically its TraderTraitor subunit, as the preliminary attribution. 

 The indicators were consistent with prior state-sponsored campaigns: Tornado Cash pre-funding, self-deleting malicious binaries, the precision of a multi-stage infrastructure attack that left no loose ends on the way out.

 On-chain analysts added another layer.

 tanuki42 flagged that KelpDAO proceeds were already commingling with funds from prior TraderTraitor operations , the 2025 BTCTurk hack and Bybit, pointing to the same third-party laundering infrastructure being reused across campaigns.

 These aren't isolated incidents sharing a name. They share operational teams, money movement protocols, and increasingly, a target profile. 

 Drift was the eighteenth DPRK-attributed crypto operation tracked by Elliptic in 2026 . KelpDAO came just over 2 weeks later. 

 That number had crossed $300 million before April ended , and that figure was published before KelpDAO pushed it closer to $600 million.

 The evolution in approach is what makes this one worth studying separately from the rest of the Lazarus ledger. 

 Drift, which KelpDAO overtook as 2026's largest hack by just a few million dollars, was a six-month social engineering operation . 

 Attackers attended conferences , built professional relationships with contributors, deposited $1 million of their own capital into the protocol, and waited. The entry point was human . The weapon was patience.

 KelpDAO required none of that. No conference badges. No Telegram rapport. No months of cover story maintenance.

 Just root-level access to a list of RPC nodes, two compromised binaries, a DDoS, and one forged packet.

 Start to finish : Under two hours. The prep time was likely longer, but the operation itself was closer to a surgical strike than a long con. 

 That's a meaningful shift. 

 Drift proved that even in-person relationships can be compromised by actors running fabricated identities.

 KelpDAO suggests the need to compromise people at all is becoming optional.

 When infrastructure can be breached and manipulated at the verification layer without touching a single human - without a phishing email, a malicious repository link, or a TestFlight app - the attack surface becomes harder to train your way out of.

 The question researchers are now sitting with is how long the preparation actually took. 

 LayerZero disclosed that the attacker obtained their RPC node list and swapped binaries on two independent clusters - nodes that were running on separate infrastructure without direct connection to each other. 

 Getting into both, undetected, with enough precision to serve forged data exclusively to one IP address while appearing clean to every other caller, suggests either a very long reconnaissance window or existing access that predated the April 18 drain by weeks or months.

 LayerZero has not explained how that access was obtained. That gap remains open.

 North Korean crypto theft exceeded $6.75 billion by the end of 2025 .

 Bybit alone accounted for $1.5 billion in February 2025. Ronin was $625 million in 2022 . 

 Drift was $285 million on April 1st . KelpDAO was $290 million seventeen days later. The pace isn't slowing. The methods are diversifying. 

 And the targets are no longer just exchanges with custodied keys, they're the infrastructure layers that connect everything else.

 What the two attacks together could suggest is a group evolving beyond isolated hacks, rapidly shifting from social engineering to exploiting structural weaknesses in crypto infrastructure. Not one-off incidents. A sustained, state-driven campaign working through whatever attack surface is cheapest to breach.

 $577 million extracted across two DeFi protocols in just over 2 weeks. Both are attributed to the same state. One required six months of groundwork. The other required a compromised RPC list. 

 If the Drift playbook required months of human infiltration and KelpDAO required none, what does the next operation look like, and which protocol is already inside it? 

## The Blast Radius

 The bridge exploit was contained to KelpDAO. What happened next was not. 

 rsETH had been whitelisted as collateral across most of DeFi's major lending markets - not because anyone was careless, but because it had earned that status. 

 Chaos Labs and LlamaRisk had reviewed it. 

 The risk parameters they set were calibrated for what rsETH had always been : A conservatively backed liquid restaking token with an uneventful price history.

 Supply caps were sized generously. Borrow caps on WETH were sized to match. Liquidation thresholds assumed the token would hold near peg.

 Every assumption was correct until 17:35 UTC on April 18th . 

 The moment 89,567 unbacked rsETH hit Aave V3 as collateral and 82,650 WETH walked out the door against it , those parameters became the mechanism of the damage rather than the protection against it. 

 The attacker didn't find a bug in Aave. They found that Aave worked exactly as designed, and designed to accommodate exactly this size of rsETH deposit.

 What made that possible : 98.5% of the collateral backing WETH borrows on Aave came from ETH LSTs. The WETH pool wasn't funding a diversified borrowing book. It was almost entirely funding levered LST carry trades. ETH depositors were effectively the third-loss layer in a concentrated structure they never explicitly signed up for.

 Within hours, WETH pool utilization hit 100%. Every deposited WETH was on loan. Nothing remained for withdrawals.

 Think of it like a pawn shop. Someone walks in with a bag of counterfeit gold, gets a loan of real cash against it, and leaves. The shop is now holding worthless collateral and the cash is gone. 

 Every other customer who stored real valuables there can't access them, not because their collateral failed, but because the shop's available cash was already out the door. That's what 100% utilization looks like from the outside. 

 What followed was a straightforward bank run: Users who understood what had happened moved first, and users who moved first got out whole. Everyone else waited.

 MEXC withdrew $431 million. 

 Abraxas Capital withdrew $392 million.

 A whale tagged to Nonco pulled $405.7 million. 

 By the time the exodus finished, $8.45 billion had left Aave in 48 hours , driving a $13.21 billion decline in broader DeFi TVL. 

 Aave's own token fell 18% within the first day . The protocol dropped from its position as DeFi's largest lender as the TVL print erased billions in a single weekend. 

 aWETH, ordinarily pegged near 1:1 with WETH, traded at an 8% discount as depositors priced in impairment. Aave's share of DeFi lending deposits fell from roughly 68% to under 61% in four days, the lowest level in over a year.

 The WETH crunch spread sideways. As ETH pools dried up, users trapped in Aave found themselves unable to exit. Some borrowed against their own stablecoin deposits instead - not because they wanted leverage, but because it was the only way to access liquidity.

 That created a $300 million secondary borrowing surge on USDT collateral in under 24 hours.

 Monetsupply, head of strategy at Spark : "We're now seeing some negative secondary effects of illiquidity in Aave stablecoin markets. Because users can't withdraw due to 100% utilization, there has been a ~$300 million increase in borrowing with USDT collateral in just the past day since the rsETH exploit." 

 Aave published its formal incident report on April 20 , outlining two scenarios depending on how KelpDAO allocates losses. 

 Under uniform socialization across all rsETH holders , the depeg sits at roughly 15% and Aave faces approximately $123.7 million in bad debt - with Ethereum Core absorbing $91.8 million of it.

 Under the harsher scenario , where losses are isolated to L2 rsETH only, the haircut on L2 collateral reaches 73.54% and bad debt climbs to $230.1 million, concentrated on Mantle, Arbitrum, and Base. Which scenario materializes depends entirely on decisions KelpDAO has not yet made.

 One clarification Aave did make : The adapter drain affected only the cross-chain float, the bridged copies on L2s. Mainnet rsETH is backed by Kelp's underlying ETH staking deposits, which the exploit never touched.

 That distinction matters for the bad debt math: If KelpDAO allocates losses only to L2 rsETH holders, Ethereum Core's exposure shrinks dramatically. 

 If losses are socialized uniformly across all chains, mainnet holders take a haircut they have a reasonable argument they didn't sign up for. 

 The question of who absorbs what had three proposed answers by Monday morning.

 DeFiLlama co-founder 0xngmi outlined them publicly : Socialize losses across all users; isolate losses entirely to L2 holders - what he called "rugging rsETH holders on L2s"; or attempt to return balances to a pre-exploit snapshot, which he described as "very hard to do" given how much the funds had moved.

 KelpDAO has not yet committed to any scenario so far. Until they do, every protocol sitting on rsETH collateral is modeling against two futures simultaneously.

 One detail that went largely unreported in the immediate coverage : In February 2025, during Aave governance discussions around listing rsETH on Arbitrum and Base, BGD Labs explicitly flagged the risks of relying on a single DVN and recommended a multi-DVN configuration. 

 That recommendation was disregarded . The risk was documented, surfaced through the correct governance channel, and set aside. Fourteen months later, the outcome that warning described played out at $290 million scale. 

 The attacker's Aave positions remain open. The rsETH posted as collateral cannot be redeemed at KelpDAO while contracts are frozen. It will not trade near peg once the scale of the unbacked supply is digested by the market. There is no profitable liquidation path for any of it.

 The bad debt is sitting in the protocol , accruing interest on borrowed positions that will never be repaid, waiting for governance to decide who absorbs it.

 Aave's Umbrella insurance fund holds 23,507 aWETH , roughly $54 million , covering only a portion of the $91.8 million Ethereum Core shortfall under Scenario 1.

 But by the time the incident report was published, approximately 80% of that module, around 18,922 of the 23,507 aWETH, had already entered the unstaking cooldown queue. 

 Stakers were attempting to exit before the module could be deployed as a backstop, draining the very buffer it was designed to protect. 

 Aave's service providers moved to recommend an immediate pause of the Umbrella module to stop further capital flight.

 The DAO treasury holds $181 million and has received ecosystem commitments to backstop further.

 Under Scenario 2 , none of that is automatically triggered, and the L2 markets are largely on their own.

 On April 21, Aave took a first step toward normalization : WETH reserves on the Ethereum Core V3 market were unfrozen, allowing users to supply WETH again, though WETH LTV remains at zero. WETH reserves on Ethereum Prime, Arbitrum, Base, Mantle, and Linea remain frozen. 

 Beyond Aave, the freeze list grew through Saturday night and into Sunday morning. 

 SparkLend, Fluid, Euler, Aave V3, Athena, Compound, Yearn, LayerZero, Pendle, Beefy and Upshift all paused rsETH markets.

 Lido disclosed $21.6 million in rsETH exposure through its EarnETH product , roughly 9% of the vault, with a $3 million first-loss buffer funded by the Lido DAO treasury standing by if needed.

 As of April 23, EarnETH deposits and withdrawals remain paused while the resolution process is finalized, with the vault curator working to deleverage affected positions .

 Morpho's CEO Paul Frambot noted about $1 million in exposure across two isolated markets , the isolated architecture preventing any propagation to adjacent vaults, the one clean example of blast radius containment in the entire incident. 

 Then came the second wave - protocols with no rsETH exposure at all that froze anyway, because their bridge infrastructure ran on LayerZero and they couldn't yet confirm their own configurations were safe. 

 Ethena paused its LayerZero OFT bridges for six hours.

 EtherFi paused weETH and eETH bridging.

 Curve paused CRV bridging across BNB, Sonic, Avalanche, Fantom, Kava and Etherlink.

 WBTC OFT via Layerzero was paused. 

 TRON , Pengu , MOCA Foundation , ApeChain , Morpho token on Arbitrum , and Solv Protocol all followed with their own pauses. 

 One researcher posted a running thread of protocols pausing LayerZero interop and stopped counting at 31.

 The real number was higher.

 Brale, a stablecoin infrastructure provider that operates its own LayerZero DVN, published something notable in the aftermath : Their DVN had also been deployed as a single node. When they read the KelpDAO incident statement and recognized the antipattern, they shut it down Saturday night. No Brale customer was impacted.

 But the candor of their disclosure made a point nobody else was making directly: KelpDAO was not the only 1-of-1 deployment in production . It was just the one that got hit. 

 The final count depends on how you measure it. 

 Exposure to locked Aave liquidity extended to : Mellow ($338M), Avant ($310M), Upshift ($302M), Kiln ($245M), CIAN ($199M), Mantle ($164M), World Liberty Financial ($123M), YuzuMoney ($80M), MidasRWA ($46.6M), templedao ($62M), ForesightVen ($50M), Resolv Labs ($33M) and others still calculating their numbers.

 DeFiLlama's broader TVL gauge lost $13.21 billion in 48 hours across the ecosystem.

 Mantle was among the first named parties to step toward the table on recovery. Mantle confirmed on April 21 that it is actively coordinating with Aave and affected protocols on a structured recovery plan, including potential participation from the Mantle treasury to support ecosystem stability.

 Given that Mantle faces the largest proportional shortfall under Scenario 2, at a 71.45% WETH shortfall , it is worth noting that recovery coordination is also in Mantle's direct financial interest.

 By April 24, Mantle was among nine named ecosystem partners - alongside EtherFi, Ethena, Lido, Golem, Ink Foundation, Tydro, Frax, and LayerZero - that had each committed in best capacity to the DeFi United recovery effort .

 Aave's contracts functioned perfectly. Every risk parameter was set by professionals who had done the work. 

 When the collateral itself is the weapon, what exactly does a risk framework protect against? 

## The Blame War

 The drain finished at 17:35 UTC on April 18th. By Monday morning, a second fight had started - this one in public, between the two parties that shared the infrastructure that failed. 

 LayerZero moved first. Their incident statement, published April 19th , described the attack in detail and attributed it to Lazarus Group. Then came the accountability framing. 

 "LayerZero and other external parties previously communicated best practices around DVN diversification to Kelp DAO. Despite these recommendations, Kelp DAO chose to utilize a 1/1 DVN configuration. A properly hardened configuration would have required consensus across multiple independent DVNs, rendering this attack ineffective even in the event of any single DVN being compromised."

 The subtext was clear. KelpDAO was warned. KelpDAO didn't listen. The infrastructure that got breached was LayerZero's, but the configuration that made the breach catastrophic was KelpDAO's choice.

 KelpDAO's rebuttal landed the same day , and it had a different story to tell. 

 "The 1-of-1 DVN setup is the configuration documented in LayerZero's documentation and shipped as the default for any new OFT deployment. Kelp has operated on LayerZero infrastructure since January 2024 and has maintained an open communication channel with the LayerZero team throughout. The question of DVN configuration came up during Kelp's L2 expansion, and defaults were affirmatively confirmed as appropriate at that time." 

 Two statements. Both internally consistent. Directly contradicting each other on the central question of who bore responsibility for the configuration.

 KelpDAO also made a point LayerZero's incident statement had not fully engaged with: “This was an attack on LayerZero's infrastructure. Kelp's own systems were not involved in building or operating that infrastructure.”

 Not a third-party verifier that KelpDAO had selected. Not a provider they had vetted independently. LayerZero Labs' DVN, running on LayerZero Labs' RPC nodes, breached by an attacker who obtained LayerZero Labs' internal RPC node list.

 The argument that KelpDAO should have diversified away from LayerZero's own infrastructure as a defense against LayerZero's own infrastructure being compromised was, at minimum, a complicated one to make. 

 CoinDesk had previewed the memo before it was published. The scoop tweet landed before KelpDAO's official statement. 

 CoinDesk reported that approximately 40% of applications currently running on LayerZero operate on 1-of-1 configurations.

 A separate on-chain analysis of ~3,500 LayerZero V2 OApp deployments over 90 days found 1,111 running a strict 1-of-1 DVN, with 28 of those having bridged more than $100,000, and 10 had bridged more than $1 million. 

 Different methodologies, similar story.

 The Dune dashboard tracking LayerZero OApp DVN configurations confirmed the picture : Single-DVN deployments were not an outlier. 

 They were widespread , across protocols of varying sizes, many of them using LayerZero Labs as the sole required verifier - the same address, the same infrastructure, the same single point of failure that had just cost KelpDAO $290 million. 

 Among the most pointed observations : Banteg published a list of protocols still running 1-of-1 configurations in the aftermath.

 Bartek.eth noted that in a scan of 185 LayerZero apps , only 10 had changed the default security settings, and of those, precisely one verified contract had changed both Oracle and Relayer - an experimental deployment by L2Beat . Every other production app had shipped the defaults and left them there.

 LayerZero's counter was that the protocol's architecture is explicitly modular - applications own their security configuration, and LayerZero's role is to provide the infrastructure, not to enforce configuration choices.

 LayerZero's position was that they had communicated multi-DVN best practices to KelpDAO directly , and that KelpDAO chose to maintain the 1-of-1 setup regardless. 

 KelpDAO's counter was that the communications channel had been open since July 2024, that no specific recommendation to change the rsETH DVN configuration had been made, and that during the L2 expansion conversation, the default was confirmed as appropriate at the time. 

 Both statements can be true. Documentation can show a minimal example while verbal guidance recommends something more robust. A team can receive that guidance and still deploy the default. None of it changes the on-chain outcome.

 LayerZero's announced consequence : They will no longer sign or attest messages for any application using a 1-of-1 DVN configuration.

 They are reaching out to all applications with 1/1 DVN configurations to migrate to multi-DVN setups with redundancy.

 That policy shift, announced after the breach , not before it, is the clearest admission in the public record that the default was insufficient for production use at scale.

 CoinDesk noted Kelp DAO's memo framed the situation as relying on LayerZero's documentation, default configurations, and team guidance when setting up the bridge , language that reads less like an incident statement and more like the opening argument of a liability claim.

 LayerZero's documented default was what a significant share of their ecosystem ran in production. KelpDAO was among them. 

 When the default is the thing that failed - who wrote it, and what writing it implied - could that be a question answered in a courtroom rather than a post-mortem? 

 $290 million is gone . 

 KelpDAO published a recovery accounting on April 24 : The initial shortfall was 163,200 ETH. Kelp recovered 40,300 rsETH (~43,000 ETH) independently. 

 The Arbitrum Security Council [secured another 30,700 ETH.

 Remaining shortfall : Approximately 89,500 ETH.

 Confirmed public commitments from Mantle, Stani, EtherFi, Lido, and Golem total 43,500 ETH toward closing that gap . Ethena, Ink Foundation, Tydro, Frax, and LayerZero have each committed in their best capacity.

 Aave and partners have launched a coordinated recovery initiative called "DeFi United" - Stani Kulechov pledged 5,000 ETH personally, EtherFi proposed 5,000 ETH, and Lido proposed 2,500 stETH. 

 As of April 24, Aave's TVL is approaching $15 billion , down from $26 billion at the time of the exploit. 

 The attacker's 75,700 ETH has been fully converted to Bitcoin in under 36 hours , primarily through THORChain, the exit is complete.

 The two parties who shared the infrastructure that failed are still arguing about whose fault it was in public statements their lawyers have almost certainly reviewed.

 KelpDAO's contracts remain paused. rsETH's backing across 20-plus chains is unresolved until the team publishes a reconciliation that nobody has seen yet.

 Aave is sitting on somewhere between $123 million and $230 million in bad debt , the spread between those two numbers depends entirely on decisions KelpDAO has not made. 

 Aave re-paused rsETH reserves across Ethereum Core, Arbitrum, Base, Mantle, and Linea on April 23 - "with the objective of recovering additional funds as the recovery plans progress. 

 Umbrella stakers on Ethereum WETH are braced for near-total slashing , the Ethereum WETH deficit is roughly twice the size of the vault, meaning the entire module gets slashed to its minimum-assets floor.

 Arbitrum WETH suppliers have no backstop at all - Umbrella does not cover L2 deployments, and the Arbitrum deficit flows directly to DAO-level mechanisms.

 The governance conversation about AAVE issuance to cover the residual is the most politically palatable option available , which means existing token holders will dilute for a breach that didn't touch a single line of Aave's code.

 Roughly $71 million in ETH was frozen by the Arbitrum Security Council , a result that would have seemed impossible two weeks ago and that still makes decentralization advocates uncomfortable. 

 $175 million is already further into Bitcoin rails than any blockchain investigator is likely to follow it. 

 LayerZero has announced it will stop signing for 1-of-1 configurations , a policy that should have existed before $290 million walked out the door, not after.

 Banteg published a list of protocols still running the same configuration KelpDAO was using when this happened . That list is long.

 The damage this exploit produced will take months of governance, legal maneuvering, and loss socialization to unwind, and some of it will never unwind.

 What's frightening here is not the dollar amount, and it's not the Lazarus attribution - both of those fit an established pattern. 

 This makes for a scary attack surface. Drift required six months of human infiltration . KelpDAO required a node list, two compromised binaries, a DDoS, and one packet. 

 The trend is toward less human contact required, not more.

 The infrastructure layer is the frontier now, and most of the industry is still writing post-mortems about the layer below it.

 DeFi composability is the feature that made rsETH worth holding across 20 chains .

 It's also the feature that turned a bridge exploit into a $200 million bad debt crisis at a protocol that wasn't hacked . 

 One forged packet. Thirteen billion dollars in ecosystem TVL erased in 48 hours. 

 Protocol after protocol freezing bridges that had nothing to do with rsETH, because the trust model underneath all of them had just cracked.

 The industry's response to every incident of this kind follows the same arc: Shock, incident report, a few weeks of governance discussion, and then back to building as if the next team won't be targeted the same way.

 LayerZero's 1-of-1 prohibition will migrate some applications to safer configurations. But what about the ones that have already been quietly compromised? 

 One compromised DVN. One forged packet. $290 million. Who else is one DVN away? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

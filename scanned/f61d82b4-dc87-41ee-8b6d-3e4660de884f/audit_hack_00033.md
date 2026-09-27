# [C] Balancer - Rekt II exploit: PeckShield's running tally marked it as one of 2025's largest DeFi exploits before most people finished their morning coffee

## Summary
Severity: Critical
Target: Balancer - Rekt II
Loss: $128,000,000
Published: 11/3/2025
Source: https://rekt.news/balancer-rekt2
Type: rekt-postmortem

## Details
## Balancer - Rekt II

 Friday, November 14, 2025 Balancer - Rate Manipulation - Rekt 

 read this article also in : 

 One rounding direction. Several blockchains. Over $128 million gone in just over an hour. 

 PeckShield's running tally marked it as one of 2025's largest DeFi exploits before most people finished their morning coffee. 

 Balancer's Composable Stable Pools weren't just exploited - they were mathematically dismantled by an attacker who found the one bit that mattered.

 November 3rd began with a rounding error so subtle the developers had left a comment in the code calling it "expected to be minimal" - an error that attackers weaponized through rate manipulation .

 The flaw? Balancer's scaling function ignored its own rounding rules.

 One direction. Always rounding down. The function that should have been bidirectional wasn't. 

 That single directional choice in the _upscale() function became a $128 million precision heist executed across multiple chains while whitehats scrambled, validators halted entire networks, and several protocol forks discovered they'd inherited the same fatal flaw. 

 Balancer had been battle-tested since 2020, processing billions in volume.

 In 2022, Certora formally verified key solvency properties in Balancer V2 - ensuring that BPT supply couldn’t exceed total assets and no new BPT could be minted without underlying deposits - but those proofs didn’t cover rounding-direction risks.

 Trail of Bits had flagged similar rounding concerns in Linear Pools nearly four years earlier.

 But somewhere between "aggregate conservation of balances" and "local compositional properties," between high-level audit scope and low-level arithmetic reality, lurked an attack vector that turned composability into contagion and deferred settlement into a precision weapon. 

 When developers write "the impact of this rounding is expected to be minimal" directly above the function that just lost $128 million, what exactly counts as catastrophic? 

 Credit: Decrypt , Certora , Coinspect , Balancer , Trail of Bits , PeckShield , Lookonchain , Berachain , Sonic Labs , Gnosis , Bankless , StakeWise , Bitfinding , Tikkala Security , William Li , Checkpoint Research , Quill Audits , Conor Grogan , OpenZeppelin , Blocksec , CoinDesk , DappRadar , Venus Protocol , Haseeb 
 07:46 UTC - Hypernative's monitoring systems caught the first abnormal swap patterns bleeding through Balancer's Composable Stable Pools. 

 Almost 30 minutes later, PeckShield's alert hit Twitter : "Hi Balancer, you may want to take a look."

 Polite. Understated. Peckshield followed up five minutes later with a number that made everyone's morning coffee go cold: "$70.8M drained."

 Lookonchain jumped in shortly after with real-time tracking across wallet addresses - $98 million , then climbed up to $116.6 million within minutes .

 Certora's engineers were already deep in the code by then , racing to identify whether this was access control, reentrancy, or something they hadn't seen before. 

 Within 20 minutes of the first alert , Hypernative's emergency controls had triggered across every affected network. 

 One minute later , every CSPv6 pool Balancer could pause was frozen.

 Recovery Mode activated . The factory that created vulnerable pools - disabled.

 But here's the problem with decentralization as a feature rather than a bug: Composable Stable v5 pools had expired pause windows .

 Years-old contracts, still processing millions in volume, now completely exposed .

 Balancer's war room coordinated containment, communications, and recovery across networks, while the attacker methodically worked through pool after pool. 

 Ethereum, Base, Arbitrum, Polygon, Avalanche, Gnosis, Berachain, Sonic and Optimism. The same exploit pattern, replicated across chains like a virus finding identical vulnerabilities in cloned hosts. 

 2 hours after the exploit started, Berachain's validators made an unprecedented call : halt the entire network. Not pause a protocol - stop the blockchain.

 Their BEX exchange was built on Balancer v2 code, and $12.86 million were rescued by a white hat during the exploit . The only solution was an emergency hard fork to roll back the damage.Those funds were later recovered .

 Sonic Labs deployed their new security mechanism on the Beets Protocol , freezing attacker addresses and zeroing out balances.

 Gnosis restricted outbound bridge activity .

 Polygon validators started censoring the attacker's transactions outright , effectively freezing assets on-chain through coordination rather than code. 

 Over eight hours into the chaos - Balancer's official Twitter account finally confirmed what everyone already knew : "Today, around 7:48 AM UTC, an exploit affected Balancer V2 Composable Stable Pools." 

 The damage assessment was still climbing. PeckShield's running tally hit $128.64 million .

 StakeWise was executing emergency multisig calls , clawing back 5,041 osETH ( $19M) and 13,495 osGNO ( $1.7M) - about 75% of what the attacker had stolen from their pools.

 BitFinding's bots intercepted another $600,000 .

 Base MEV bots recovered $150,000 more. 

 But the attacker had a head start, a working exploit, and something almost nobody else had: a complete understanding of how Balancer's math broke at the boundaries. 

 Within roughly an hour of the first exploit, copycat transactions started appearing.

 The attacker had already published a deployed auxiliary contract on-chain, providing anyone who could read Solidity a blueprint for exploitation: change the pool address, change the sender address, deploy, profit.

 27 forks of Balancer V2 inherited the same logic flaw - many of which still had live liquidity. Not all were so lucky.

 Tikkala Security noted that even a week after the initial exploit, the copycat attacks are continuing . 

 When one protocol's vulnerability becomes several forks' catastrophes, and copycats are still exploiting the same bug a week later, is open-source DeFi's greatest feature or its fatal flaw? 

## Where Precision Goes to Die

 Most exploits announce themselves with reverted transactions and emergency warnings. 

 This one was hiding in a scaling function. 

 Deep in BaseGeneralPool.sol , past the access controls and the flashloan guards and the reentrancy checks, sits a function called _upscale().

 It runs before every swap. Takes tokens with different decimals - USDC's 6, DAI's 18, WBTC's 8 - and normalizes everything to 18-decimal precision so Balancer's invariant math works.

 Mundane infrastructure. The kind of code that survives four years and a dozen audits because it's too boring to break.

 Balancer's developers knew precision mattered, they weren't careless. 

 They'd built an entire rounding library - FixedPoint - with explicit functions for rounding up (mulUp) and rounding down (mulDown). 

 The design principle was clear: rounding direction should favor the protocol. Round down when receiving tokens, round up when sending them.

 The _upscale() function only used mulDown - always rounding in one direction regardless of context.

 Always favor the protocol.

 Except in one place.

 Here's what the developers wrote : 

 "Upscale rounding wouldn't necessarily always go in the same direction... This is the only place where we round in the same direction for all amounts, as the impact of this rounding is expected to be minimal." 

 They chose mulDown . Wrote a comment explaining why. Called the impact "minimal." 

 And for 99.9% of swaps, they would have been right.

 But this attacker wasn't interested in normal swaps.

 How Rounding Becomes Theft... 

 When you swap Token A for Token B in a Balancer pool , the contract scales your input amount to 18 decimals, calculates how much Token B you should receive, then scales that back down to Token B's actual decimal representation. 

 If Token B has 6 decimals and you're supposed to receive 1,234,567 scaled units, the pool divides by 10^12 to get back to 6-decimal precision.

 That division creates a remainder - and remainders mean choices about rounding.

 Traditional AMM design says: round against the user, in favor of the pool . If there's any precision loss, the protocol keeps it. 

 But Balancer's _upscale() function rounded down before the invariant calculation . That meant the pool was working with slightly smaller numbers than it should have been. 

 The invariant - the mathematical constant that ensures the pool stays balanced - was computed using slightly understated token amounts .

 In a normal swap, this off-by-one discrepancy is negligible, disappearing into typical gas costs and slippage.

 But Composable Stable Pools aren't normal pools.

 And the attacker knew exactly which abnormal features to weaponize. 

 They used Composability as a weapon. 

 Balancer's flagship feature was treating LP tokens (BPT) as tradeable assets within the pool itself. You could swap DAI directly for BPT in the same transaction, creating recursive liquidity structures that let users move between pools without explicitly withdrawing.

 Combined with Balancer's "deferred settlement" architecture - where tokens don't actually transfer until the end of a batch transaction - this created a perfect storm.

 The attacker exploited Balancer’s internal‑balance mechanics to temporarily obtain BPT within the same batchSwap (a deficit/“internal credit” state), using those ephemeral BPT claims to swap for underlying tokens and push pool balances into edge‑case low levels before settling.

 This behavior is effectively a transaction‑local “flash‑mint” of BPT via the Vault’s internal accounting. 

 The Attack Math is as follows. 

 Deploy the calculation contract - A separate contract to handle complex precision math and avoid stack depth issues.

 Flash-mint massive BPT - Use Balancer's composability to create LP tokens without depositing assets.

 Drain the pool to minimum liquidity - Swap BPT for underlying assets , pushing pool balances to edge cases where rounding matters.

 Execute the precision exploit - target token/scale combos that make the upscaling remainder as big as possible. Because _upscale() uses mulDown, each swap quietly cheats the invariant a little - and composability turns those little cheats into a heist.

 Amplify through iteration - repeat the micro‑swap loop dozens of times in a single transaction ( on‑chain traces show 65+ micro‑swaps ), letting tiny per‑iteration losses compound into a material invariant deflation.

 Extract value - The pool's invariant is now desynced from reality - BPT is worth more than the underlying assets should support .

 Burn BPT for profit - Redeem the inflated BPT for real assets , leaving the pool insolvent.

 The elegant brutality of it: every step was a valid operation.

 Just math, executed at the boundaries where precision loss accumulates. 

 When the code comment says "minimal impact" and the attacker sees "maximum opportunity," whose math was wrong? 

## The Precision Heist

 The blockchain receipts don't show a hack. 

 They show valid transactions. Approved swaps. Legitimate withdrawals. 

 No leverage tricks. No reentrancy. Just arithmetic collapse.

 Just someone who understood Balancer's math better than the people who wrote it.

 Attacker Addresses are as follows. 

 Ethereum: 

 Primary: 

 0x506D1f9EFe24f0d47853aDca907EB8d89AE03207 

 Secondary: 

 0xAa760D53541d8390074c61DEFeaba314675b8e3f 

 Intermediary: 

 0x766a892f8ba102556c8537d02fca0ff4cacfc492 

 Arbitrum: 

 0x506D1f9EFe24f0d47853aDca907EB8d89AE03207

 0x310ebc4ffe858ab40b95343de0c2431b95892962

 0x0000000000004f3d8aaf9175fd824cb00ad4bf80 

 Base: 

 0x506D1f9EFe24f0d47853aDca907EB8d89AE03207 

 Optimism (Beethoven X): 

 0x506D1f9EFe24f0d47853aDca907EB8d89AE03207

 0x872757006b6F2Fd65244C0a2A5fdd1f70A7780f4 

 Polygon: 

 0x506D1f9EFe24f0d47853aDca907EB8d89AE03207 

 Sonic (Beets): 

 0x506D1f9EFe24f0d47853aDca907EB8d89AE03207 

 Consolidation Addresses: 

 0x872757006b6f2fd65244c0a2a5fdd1f70a7780f4 (Arbitrum profits)

 Attack Contracts are as follows. 

 Math Helper Contract (deployed on-chain, publishing the exploit method for copycats): 

 0x679B362B9f38BE63FbD4A499413141A997eb381e 

 Ethereum Coordinator Contract: 

 0x54B53503c0e2173Df29f8da735fBd45Ee8aBa30d 

## The Two-Stage Attack

 Two transactions. The first looked clean - no profit extracted, nothing obviously wrong. The second collected the payday. 

 Splitting the operation kept automated monitoring systems quiet during the actual exploit. 

 By the time the withdrawal hit, understanding what happened required reconstructing the entire attack sequence.

 Stage 1: Manipulation 

 Run the precision-loss loop. Drain the pools. Park everything in Balancer Vault's internal balance ledger where external queries can't see it. 

 Stage 2: Extraction 

 Call manageUserBalance(WITHDRAW_INTERNAL). Convert internal credits to actual tokens. Walk away.

## Ethereum - The Main Event

 Several pools. Nearly 25,000 ETH stolen. 

 Primary Attack TX: 

 0x6ed07db1a9fe5c0794d44cd36081d6a6df103fab868cdd75d581e3bd23bc9742 

 Withdrawal TX: 

 0xd155207261712c35fa3d472ed1e51bfcd816e616dd4f517fa5959836f5b48569 

 The following pools were drained. 

 osETH/WETH Pool 

 Pool ID: 
 0xdacf5fa19b1f720111609043ac67a9818262850c000000000000000000000635 

 Contract: 
 0xDACf5Fa19b1f720111609043ac67A9818262850c 

 Drained: 4,623 WETH + 6,851 osETH ≈ 11,474 ETH

 wstETH/WETH Pool 

 Pool ID: 

 0x93d199263632a4ef4bb438f1feb99e57b4b5f0bd0000000000000000000005c2 

 Contract: 

 0x93d199263632a4EF4Bb438F1feB99e57b4b5f0BD 

 Drained: 4,259 wstETH + 1,963 WETH ≈ 6,222 ETH

 rsETH/WETH Pool 

 Pool ID: 

 0x58aadfb1afac0ad7fca1148f3cde6aedf5236b6d00000000000000000000067f 

 Contract: 

 0x58AAdFB1Afac0ad7fca1148f3cdE6aEDF5236B6D 

 Drained: 1,192 rsETH + 891 WETH ≈ 2,083 ETH

 weETH/rETH Pool 

 Pool ID: 
 0x05ff47afada98a98982113758878f9a8b9fdda0a000000000000000000000645 

 Contract: 

 0x05ff47AFADa98a98982113758878F9A8B9FddA0a 

 Drained: 703 rETH + 495 weETH = 1198 ETH

 wstETH/rETH/sfrxETH Pools 

 Pool #1: 

 0x5aee1e99fe86960377de9f88689616916d5dcabe000000000000000000000467 

 Contract: 

 0x5aEe1e99fE86960377DE9f88689616916D5DcaBe 

 Drained: 4 ETH

 Pool #2: 

 0x42ed016f826165c2e5976fe5bc3df540c5ad0af700000000000000000000058b 

 Contract: 

 0x42ED016F826165C2e5976fe5bC3df540C5aD0Af7 

 Drained: 191 wstETH + 2148 sfrxETH + 220 rETH = 2559 ETH

 ezETH/WETH Pool 

 Pool ID: 

 0x596192bb6e41802428ac943d2f1476c1af25cc0e000000000000000000000659 

 Contract: 

 0x596192bB6e41802428Ac943D2f1476C1Af25CC0E 

 Drained: 751 ezETH + 442 WETH = 1,193 ETH

 Total Drained on Ethereum Pools: 24,733 ETH (Worth roughly $91.5 million at the time of the theft)

## Arbitrum

 Primary Attack TX: 

 0xe4dfc8b8b54eb7e101d59cd9f87f389186b2e8f6e188557ae9dfdbea2b12e703 

 Withdrawal TX: 

 0x4e5be713d986bcf4afb2ba7362525622acf9c95310bd77cd5911e7ef12d871a9 

 Additional Attack TXs: 

 0x5258dcfdd5fa04a81648e1e6d8caffd7438cf27d6bcfc8d1cb0e8c005307eee1

 0x962e95dfa66936d96c25e75cf7aba023e0486b3d63f477664899dbbf54d7aa86

 0xfe3d66d50b4f837994d0a06220e3b14f7652e79c12bc92362f6a760b630c6999 

 The following pool was drained. 

 wstETH/rETH/cbETH Pool 

 Pool ID: 

 0x4a2f6ae7f3e5d715689530873ec35593dc28951b000000000000000000000481 

 Contract: 

 0x4a2F6Ae7F3e5D715689530873ec35593Dc28951B 

 Drained: 462 ETH

 Proceeds consolidated to 0x872757006b6f2fd65244c0a2a5fdd1f70a7780f4 , then bridged back to Ethereum via Stargate.

 Arbitrum Total: 462 ETH (Worth $1.7 million at the time)

## Base

 Attack Contract: 

 0x56e5Adab68b594B0c2aD6C112D94AE5aCA98A001 

 Primary Attack TX: 

 0x29135f912d67db38478d0be70b9f2a1fab3b121b74d776f835ac66d6df134ec5 

 The following pools were drained. 

 rETH/WETH Pool 

 Pool ID: 

 0xc771c1a5905420daec317b154eb13e4198ba97d0000000000000000000000023 

 Contract: 

 0xC771c1a5905420DAEc317b154EB13e4198BA97D0 

 Attack TX: 

 0xe9245fb124c3a6ff6a0e39c6d0db02b74b3a3d805f6bf016f4b9ac56cbfb73ae 

 Drained: 17 WETH + 24 rETH = 41 ETH

 weETH/wETH Pool 

 Pool ID: 

 0xab99a3e856deb448ed99713dfce62f937e2d4d74000000000000000000000118 

 Contract: 

 0xaB99a3e856dEb448eD99713dfce62F937E2d4D74 

 Attack TX: 

 0x927c9e6d9fc26b2ee13b88f553701a4e7514f8220d34e6517c634ddd135cd874 

 Drained: <1 ETH

 cbETH/WETH Pool 

 Pool ID: 

 0xfb4c2e6e6e27b5b4a07a36360c89ede29bb3c9b6000000000000000000000026 

 Contract: 

 0xFb4C2E6E6e27B5b4a07a36360C89EDE29bB3c9B6 

 Attack TX: 

 0xd61f26bd435b31f781165a522fc78a040f864eafc74e07f86314ca265d96287d 

 Drained: <1 ETH

 Base Total: 42 ETH (~$155K at $3,700/ETH)

## Optimism (Beethoven X)

 Attack Transaction: 

 0x3c9d2d16404a79feed9876a79f168af334726ad3ee1371f581d50ebebfe6b8c6 

 Withdrawal Transaction: 

 0xbd417633433e45c1dddf9fac7680f86dfde832c07b93f4de5ce69c6312d19381 

 Optimism Total: ~$1.3 Million

## Polygon

 Attack Transaction: 

 0x167993d4cc39771923a6cd11d2d6e73a1b68c7464ea3c76ba41fbd32df7a96da 

 Withdrawal Transaction: 

 0x9630b26a49c451365989cbd2d9696ea3bdf02505bcb297b6239f330f114c9673 

 Polygon Total: ~$390K

## Sonic (Beets)

 Attack Transaction: 

 0xd7996c8e187b9bd539a04a4f39de4d8c7c1670c601134329937738b4dfa6f8ad 

 Withdrawal Transaction: 

 0xc0cc599fa5c1ec2a43a96b018fd653783cf8dd3e6f670f94961c89b61ce8c0f9 

 Attacker moved 19.5M stS ($3M) to 0x0e9c9473D0c504Da72763426719F6f03A15544D5 using permit() and transferFrom(), then swapped to WBTC and bridged to Ethereum via LayerZero.

 Sonic Total: $3.44M

## Berachain (BEX)

 $12.86M was actively rescued by white hats when validators halted the entire chain and executed an emergency hard fork to roll back the damage. 

 Berachain Total: $12.86M (Recovered)

## Attack Summary

 Primary Exploiter Haul: 

 Ethereum: 24,733 ETH ($91.5M)

 Arbitrum: 462 ETH ($1.7M)

 Base: 42 ETH ($155K)

 Subtotal: 25,237 ETH ($93.4M)

 Fork Attacks (and recovery): 

 Sonic (Beets): $3.44M

 Berachain (BEX): $12.86M (recovered)

 Optimism (Beethoven X): $1.3 Million

 Polygon: $390K

 Gnosis, Avalanche: Possible smaller amounts - not publicly reported.

 Fork Subtotal: ~$18M

 Total Stolen: ~$128M (PeckShield, industry consensus).

 Our forensics verified: ~$111M in primary attacker withdrawals.

 Gap: ~$17M in copycat attacks and undisclosed Gnosis/Avalanche losses.

 Note: Our forensics shows $111M in verified primary attacker withdrawals. PeckShield's $128M figure could include copycat attacks, minor chains (Gnosis, Avalanche), and captures the full ecosystem damage across all networks. Know something we don't? Help us complete the picture - reach out to Rekt News with additional transaction data . 

 Current stolen funds are still in the wild sitting in the attacker’s wallets are as follows. 

 0x0e9c9473d0c504da72763426719f6f03a15544d5 ($2.6M)

 0x506d1f9efe24f0d47853adca907eb8d89ae03207 ($11M)

 0xf19fd5c683a958ce9210948858b80d433f6bfae2 ($574K)

 0xaa760d53541d8390074c61defeaba314675b8e3f ($20M)

 0x0e9c9473D0c504Da72763426719F6f03A15544D5 ($2.6M)

 0x1c7da4e9740f99279c193540328314c04e2edc00 ($22k)

 0x045371528A01071D6E5C934d42D641FD3cBE941c ($520k)

 Still sitting in the Attacker’s known wallets: Roughly $37 million.

## The Copycat Wave

 Within 53 minutes of the first attack, copycats started appearing. 

 First Copycat TX: 

 0x14fb45dd869208edffcb221add152a20292283be172ddb6ccfd2d73e3710b6f4 

 Time: 08:39 UTC (53 minutes after initial attack)

 The attacker's math helper contract was deployed on-chain with full source code - including all the calculation logic and even Balancer's error types. Anyone who could read Solidity had a ready-made exploit kit.

 Change the pool address. Change the sender address. Deploy. Profit. 

 27 Balancer v2 forks inherited the exact same vulnerability. Some paid the price in the hours that followed. 

## The Whitehat Counterstrike

 Not everyone was looting. 

 StakeWise Recovery: Emergency multisig execution clawed back 5,041 osETH ($19M) and 13,495 osGNO ($1.7M) - roughly 73.5% of what the attacker stole from their pools.

 BitFinding: Whitehat bots intercepted $600K 

 Base MEV Bots: Recovered $150K 

 White-hat Recovery (V2 Meta-Stable Pools): Secured $4.1M into controlled custody

 Berachain Hard Fork: Recovered $12.86M 

 Total Recovered/Frozen: $38.4M

 One attacker. One exploit. Fifty-three minutes later, the copycats arrived for the scraps. 

 When your attack contract becomes the documentation for a dozen copycats, did you hack DeFi or just write the world's most expensive tutorial? 

## Battle-Tested Doesn't Mean Bulletproof

 Balancer's security credentials read like a who's-who of audit firms. 

 OpenZeppelin , Trail of Bits , Certora , and ABDK Consulting . Over a dozen audit reports between them since 2020. 

 Formal verification . ImmuneFI Bug bounties running for years . Almost half a decade of battle-testing across every major chain.

 And yet, they still got rekt.

 How did we get here?

 What the Audits Caught... 

 Certora's 2022 review of Balancer V2 Stable Pools proved high level solvency at the time . They verified that BPT supply could never exceed total assets . They proved that minting BPT required corresponding asset increases. They confirmed aggregate conservation of balances. 

 Trail of Bits had flagged rounding concerns in their 2021 audit - specifically in Linear Pools under finding TOB-BALANCER-004 .

 At the time of the audit, TOB couldn’t definitively determine whether the identified rounding behavior was exploitable in the Linear Pools as they were configured.

 They flagged the issue because they found similar ones in the first audit, and recommended implementing comprehensive fuzz testing to ensure the rounding directions of all arithmetic operations matched expectations.

 The vulnerable code?

 According to OpenZeppelin, the attack vector was first introduced on July 16, 2021 , when MetaStablePool overrode the _scalingFactors function (commit 059284e).

 The same change was applied to LinearPool on September 1, 2021 (commit 4e9e70a) and to StablePhantomPool - later renamed ComposableStablePool - on September 20, 2021 (commit f450760). 

 OpenZeppelin notes that prior audits did not cover any of these pools , leaving this attack vector unexamined. 

 The Composable Stable Pool sat on top of the same scaling math as the older pools - the _upscale() helper (which calls FixedPoint.mulDown) is the shared utility that does the heavy lifting.

 The helper’s own comment even admits the team expected the rounding hit to be “minimal.” 

 The audits weren't wrong. They were just out of scope at the time. 

 What They Missed... 

 Certora's analysis identified exactly what would have caught it. 

 Roundtrip Swap Invariance : Swapping Token A → Token B → Token A should never yield more than you started with.

 Violation of this property reveals rounding asymmetries. The kind that compounds. The kind that turns "minimal" into "maximal" when an attacker can run 65 iterations in a single transaction .

 BPT Share Value Invariant : “For any user operation, the share value of a single BPT must not decrease.” 

 This catches desynchronization between totalAssets and totalSupply - including the subtle kind that stems from rounding discrepancies and imprecise invariant calculations. 

 Certora’s 2022 audit proved solvency . It abstracted away StableMath functions to simplify proofs. The formal proofs didn’t cover numeric precision under extreme low‑liquidity or edge‑case scenarios, where rounding errors could accumulate.

 As Certora put it in their analysis : "Solvency proofs are not sufficient. Aggregate conservation of balances does not imply rounding safety."

 The Threat Landscape Evolved. 

 In 2021, when Trail of Bits reviewed Balancer, the threat model was different . Access control bugs. Reentrancy. Phishing. The usual suspects. 

 Rounding issues were considered a moderate at the time , underemphasized risk: not the most severe, but worth noting. At the time, exploits leveraging rounding hadn’t become widespread yet.

 By 2023-2024, precision exploits had become a pattern . Hundred Finance and Onyx Protocol both became victims back in 2023.

 Multiple rounding-based drains showing that arithmetic boundaries were now primary attack vectors. 

 By 2025, the playbook was clear: find the rounding edge, amplify it through composability, extract value through precision loss. 

 Abracadabra and Bunni both got hit by similar attacks earlier this year.

 As the space evolves, so do the exploits and so should we.

 Trail of Bits had flagged it as undetermined severity in 2021 because they couldn't prove exploitability at the time. That flag eventually became very red. 

 Four years later, someone proved it with $128 million. 

 Balancer's BAL token dropped 5% at the time . TVL plummeted 46% in 24 hours , from $626 million to $338 million as users scrambled to withdraw from any pool that looked remotely similar to the exploited ones.

 Venus Protocol paused BAL borrowing on Ethereum , setting loan-to-value ratios to zero.

 Then there were the Chain Responses. 

 Different blockchains, different philosophies, different emergency responses. 

 Berachain: Validators halted the entire network . Executed an emergency hard fork . Rolled back the BEX theft completely. "Code is law" took a backseat to "our users don't lose $12.86 million."

 Polygon: Validators censored attacker transactions , effectively freezing stolen assets through coordination rather than code.

 Sonic Labs: Deployed new freeze functionality mid-exploit , zeroing out attacker balances on-chain. 

 Gnosis: Restricted outbound bridge activity , trapping funds before they could escape to other chains. 

 As Haseeb Qureshi (Dragonfly) noted : "Smaller ecosystems should prioritize safety and community protection over code is law.“

 The decentralization paradox laid bare: immutability is a feature until it's a bug.

 DeFi's composability didn't just spread liquidity - it spread the vulnerability to several forks. 

 If your blockchain needs validator intervention to stop a mathematically valid exploit, did we decentralize finance or just decentralize the emergency brake? 

 Five years. Billions in volume. A dozen audits. Formal verification. Bug bounties. Battle-testing across every major chain. 

 None of it mattered when someone showed up who understood the math better than the people who wrote it. 

 Balancer's developers left a code comment calling the rounding impact "minimal" - the attacker proved them wrong to the tune of $128 million.

 The gap between what auditors prove and what attackers exploit should be closing. We are seeing less code exploits.

 Solvency proofs don't catch precision loss. High-level verification doesn't test roundtrip invariants.

 Battle-testing just means the obvious attacks failed. 

 When several forks inherit the same vulnerability and entire blockchains abandon immutability to prevent theft, maybe composability isn't the killer feature we thought it was. 

 Maybe it's just the efficient distribution mechanism for turning one protocol's bug into an ecosystem's catastrophe.

 DeFi spent years optimizing for trustlessness, only to discover that when trust fails at the math layer, validators start censoring transactions and multisigs start hitting pause buttons.

 Code was law until it cost users nine figures, then suddenly every chain remembered it had admin keys. 

 If your protocol needs several audits but still gets exploited through code added after the last one finished, and your blockchain needs validator intervention to protect users from "immutable" smart contracts, did we build the future of finance or just expensive infrastructure for teaching the same lessons over and over? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

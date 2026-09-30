# [H] Yearn - Rekt III exploit: There was an almost forgotten pool on Yearn with novel math still processing millions

## Summary
Severity: High
Target: Yearn - Rekt III
Loss: $9,000,000
Published: 11/30/2025
Source: https://rekt.news/yearn-rekt3
Type: rekt-postmortem

## Details
## Yearn - Rekt III

 Tuesday, December 2, 2025 Yearn - Unchecked Arithmetic Underflow - Legacy Code 

 read this article also in : 

 There was an almost forgotten pool on Yearn with novel math still processing millions. 

 Then someone broke the invariant, deposited dust and minted to infinity. 

 Yearn's forgotten yETH relic - a product so abandoned even the team forgot to turn it off - minted 235,443,031,407,908,519,912,635,443,025,109,143,978,181,362,622,575,235,916 tokens out of thin air .

 That's not a typo and it is a number so huge, you could probably see it from space.

 $9 million vanished in a single transaction while 1,000 ETH slipped through Tornado Cash .

 Yearn's V2 and V3 vaults remained untouched - small comfort for a protocol now sitting at three exploits and counting. 

 When legacy math can mint infinity, is the real exploit the code - or the culture that ships it? 

 Credit: Blocksec , Togbe , yearn , Peckshield , Defi Chad , Banteg , William Li , Blockscout , BanklessTimes 
 November 30th started with Togbe noticing something odd . 

 Heavy interactions with Tornado Cash . LST tokens moving in unusual patterns across Yearn, Rocket Pool, Origin, and Dinero.

 Then the numbers started breaking - yETH supply minted to infinity.

 Not an exploit in progress. Already done. 

 By the time Peckshield dropped the alert , millions were already gone. 

 The attack occurred at 21:11 UTC - a single atomic transaction that minted approximately 235 trillion yETH tokens and drained the pool completely.

 Yearn's Twitter acknowledgment came shortly after the damage was done : "We are investigating an incident involving the yETH LST stableswap pool. Yearn Vaults (both V2 and V3) are not affected."

 Almost six hours of silence before the real numbers landed.

 $8 million from the yETH stableswap pool . Another $0.9 million from the yETH-WETH pool on Curve .

 Total Damage: $9 million.

 Around 1,000 ETH ($3 million) had already been laundered through Tornado Cash . 

 The rest at the time - roughly $6 million - sat in the attacker's wallet . 

 Yearn spun up a war room with SEAL911 and ChainSecurity.

 They compared the complexity to the recent Balancer hack - another precision exploit that turned rounding errors into retirement money. Initial analysis indicated this wasn't going to be a quick explanation.

 This was not the first time yearn was exploited.

 First they were hit with an $11 million flash loan attack back in 2021 .

 Followed by an attack in 2023 , where an attacker exploited a misconfiguration in the project’s yUSDT token contract.

 The irony of the 3rd exploit was sharp: someone doing casual research stumbled across an exploit in a product Yearn had essentially forgotten existed. 

 When casual research flags what established processes didn't catch, makes one wonder which legacy products need eyes on them?" 

## The Math That Broke

 yETH wasn't just any pool - it was a custom stableswap built on complex math-heavy logic for liquid staking token aggregation. 

 Separate code from Yearn's vaults. No shared infrastructure with V2 or V3. An isolated product with novel invariant calculations that nobody was actively maintaining. 

 The attack required surgical precision.

 According to Banteg from yearn’s post-mortem and William Li's technical breakdown , the attacker didn't exploit the math - they weaponized it.

 Step One: Break the pool's reality.

 The attacker hammered the pool with remove_liquidity(0) calls - withdrawals of nothing that still triggered recalculations. 

 Virtual balances shifted without any actual assets moving. Combine that with update_rates() calls and the rounding asymmetry between pow_up and pow_down functions , and you've got a slowly corrupting invariant. 

 Each iteration drifted the relationship between balance sum (Σ) and balance product (Π) further from sanity.

 Throw in OETH's rebasing behavior - where balances change automatically - and the invariant stopped representing anything real.

 Final withdrawal state: Σ = 0, Π = 0, supply = 0. 

 Physically impossible. Mathematically toxic. But the code didn't check.

 Step Two: Trigger the detonation.

 The attacker then deposited dust - literal pocket change. 1 wei of wstETH, 1 wei of rETH, 1 wei of cbETH, and 9 wei of mETH. Total value: essentially nothing. 

 This triggered calc_supply(), a Newton-Raphson solver designed to calculate how many LP tokens to mint. The function tried to solve for a value that satisfied the corrupted invariant. 

 When the amplification factor (A = 4.5 × 10²⁰) met the impossible Σ/Π relationship , the solver hit an unchecked arithmetic underflow.

 The calculation: s' = (A Σ - s r) / (A - PREC)

 When AΣ < sr, the numerator goes negative. In EVM arithmetic, negative wraps to 2²⁵⁶, creating a number around 10⁷⁷.

 The solver iterates toward "convergence" on a massive value.

 Result: D_new ≈ 2.3544 × 10⁵⁶ 

 The pool minted exactly that many yETH tokens directly to the attacker's address. 

 Not a clever economic attack. Not an oracle manipulation. Just broken math executing exactly as written - calculating the "correct" answer to an impossible question. 

 The attacker used the counterfeit LP tokens to drain real assets through single-asset withdrawals.

 Helper contracts deployed minutes before the attack handled the heavy lifting , then self-destructed to erase the bytecode trail.

 One transaction. One block. Pool emptied.

 Banteg's post-mortem confirmed what analysts suspected: this was an unchecked underflow in a Newton solver triggered by a corrupted invariant state.

 The kind of bug that sits dormant until someone finds exactly the right sequence of operations to detonate it. 

 Fragile math and forgotten maintenance made the exploit inevitable - but what did the attacker do once the pool cracked open? 

## Follow the Trail

 The attacker didn't materialize from nowhere with a $9 million payday. 

 The seed money came through Railgun thirty minutes before execution. 

 Funding Transaction: 0x68f88d2ffcef1ceafde26fc290cf1d31ff9a461b4ee2aeb68da8aa9cf70e600c 

 Primary Attacker Address: 
 0xa80D3F2022F6Bfd0B260bF16D72CaD025440C822 

 Secondary Attacker Address: 

 0xFb63aa935Cf0a003335dCE9Cca03c4F9c0fa4779 

 Main Attack Contract (Self-Destructed): 
 0xB8e0A4758Df2954063Ca4ba3d094f2d6EdA9B993 

 Secondary Attack Contract (Helper Contract): 

 0xbb2789b418fA18f9526bA79fa7038d4e6d753f73 

 Attack Transaction: 0x53fe7ef190c34d810c50fb66f0fc65a1ceedc10309cf4b4013d64042a0331156 

 One transaction. Dust deposit. Infinite mint. Pool drain. Self-destruct.

 The exploited pool - yETH's custom stableswap - went from operational to empty in a single block. 

 The Exploited yETH Pool: 
 0x69accb968b19a53790f43e57558f5e443a91af22 

 Around 1,000 ETH (~$3M) went straight into Tornado Cash - ten deposits, 100 ETH each. No hesitation, no cool‑down period. Just the attacker laundering funds inside the same block as the exploit.

 Attacker’s Loot Wallet (the one that handled both the Tornado flows): 
 0x3e8e7533dcf69c698Cf806C3DB22f7f10B9B0b97 

 You can see the Tornado pipeline directly in the exploit transaction’s internal calls - all on Etherscan - showing the attacker batching ten 100‑ETH deposits straight into Tornado Cash from this wallet. 

 Internal calls inside the exploit TX: 

 Internal Calls on Etherscan 

 Together, these traces show exactly how the attacker chained the exploit, the liquidity drain, and the obfuscation into a single, atomic sequence - one block, start to finish, clean exit.

 But not everything stayed stolen.

 With help from Plume and Dinero teams, Yearn managed to claw back $2.33 million (857.49 pxETH) in a coordinated recovery operation.

 Recovery Transaction: 0x0e83bb95bb9d05fb81213b2fad11c01ea671796752e8770b09935f7052691c35 

 A decent grab-back, but still leaving a big chunk out in the wild.

 The Primary Attacker Address is still sitting on $3.84 million: 
 0xa80D3F2022F6Bfd0B260bF16D72CaD025440C822 

 Roughly a third laundered, a quarter recovered, and the rest left marooned, for now… 

 When your exploit leaves a cleaner paper trail than most legitimate DeFi transactions, who's really anonymous? 

## The Product Nobody Remembered

 yETH wasn't just old code. It was abandoned code still running in production. 

 Banteg laid it out plainly : "It was a separate product with quite complex/novel math; it doesn't share any code with vaults." 

 Completely isolated architecture. Custom invariant calculations that no other protocol used.

 A meta-aggregator for liquid staking tokens that Yearn had essentially stopped maintaining while V2 and V3 vaults continued getting active development and security attention.

 The contrast was brutal.

 Yearn's V2 and V3 vaults - the products people actually used - remained untouched throughout the exploit . Those systems had ongoing audits, active monitoring, and continuous development. 

 They worked exactly as designed while the legacy yETH pool imploded. 

 yETH? That was the relic nobody thought about until it started bleeding millions.

 The vulnerability targeted an outdated version of the yETH token contract , not the newer vault infrastructure that Yearn currently promotes.

 Legacy contract. Still live. Still processing millions. Just not on anyone’s radar. 

 The exploit didn’t exploit a clever new vulnerability in modern code. 

 It exposed something worse - a forgotten product with novel math running unattended until someone bothered to read the contract closely enough to break it.

 The flaw was simple in concept but catastrophic in effect: a legacy minting logic bug, a forgotten contract running old math, abandoned but live.

 Yearn’s response was textbook damage control: Spin up the war room, coordinate with Plume and Dinero for a partial recovery, and reassure users that active products were safe.

 The problem wasn't the response - it was that yETH had been running for years without anyone asking whether legacy products should still be operational. 

 When separate code becomes out of sight, out of mind, who makes sure the old systems stay safe? 

 Another reminder that forgotten code has a long memory. 

 $9 million vanished through a product nobody remembered to deprecate, drained by math nobody thought to sanity-check, in a pool nobody was actively monitoring. 

 The V2 and V3 vaults kept humming - proof that when Yearn focuses on something, it works.

 The danger wasn’t in the active products - it was in the ones still online after the team moved on.

 Legacy code isn't just technical debt; it's a loaded gun in the codebase waiting for someone curious enough to find the trigger.

 yETH proved that isolation protects active products but abandons the forgotten ones to anyone willing to read the source.

 Three exploits. Three different attack vectors. Three lessons that somehow never stick. 

 If code is valuable enough to keep running, it's valuable enough to maintain - and if it's not worth maintaining, how many more loaded guns are sitting in DeFi's abandoned repositories? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] OtterSec: Becoming a millionaire, 0.000150 BTC at a time

## Summary
Severity: High
Published: Tue, 26 Apr 2022
Source: https://osec.io/blog/spl-swap-rounding/
Type: security-research

## Details
## Becoming a millionaire, 0.000150 BTC at a time

 OtterSec Apr 26, 2022 #solana #report How we discovered a critical issue in Solanaâs stable swap implementation. A story about arbitrage and rounding.

## Introduction 

 We discovered a critical rounding issue in the Solana Program Libraryâs implementation of stable swap, spl-token-swap . Similar to Neodymeâs spl-token-lending exploit, we were able to extract a single token per instruction. This exceeds the value of the 5000 lamport transaction fee on BTC stable swaps, allowing an attacker to profitably drain funds.

 Such BTC stable swaps had over 74 million in combined value. The total value of stable swaps impacted exceeded 700 million.

 Note We would also like to thank the Saber team for their fast triage and remediation.

 Rounding bugs are an increasingly common vulnerability class, enabled by low transaction costs 

## Discovery 

 Parth, one of our researchers, was implementing a graph search for our arbitrage bot to calculate the price of any token relative to SOL.

 After a while, he noticed something weird:

 so either my graph search is wrong
or its possible to get a ton of money out of nothing

```

```
 KwnjUuZ : 0 9vMJfxu -> 1 EPjFWdd 

 KwnjUuZ : 1 EPjFWdd -> 2 9vMJfxu 

 KwnjUuZ : 2 9vMJfxu -> 3 EPjFWdd 

 HU1tejU : 3 EPjFWdd -> 625 PRT88Rk 

 24ZbKS3 : 625 PRT88Rk -> 7 EPjFWdd 

 3oRPcFa : 7 EPjFWdd -> 6 BQcdHdA 

```

```

 1 EPjFWddKwnjUuZ : 1 EPjFWdd -> 2 9vMJfxuKwnjUuZ : 2 9vMJfxu -> 3 EPjFWddHU1tejU : 3 EPjFWdd -> 625 PRT88Rk24ZbKS3 : 625 PRT88Rk -> 7 EPjFWdd3oRPcFa : 7 EPjFWdd -> 6 BQcdHdA"> 

 Somehow, we were getting tokens from nothing?

 After taking a look at the pairs on which this was occurring, we quickly realized that only stable swap pairs were impacted:

```

```
 KwnjUuZhTMTSGAaavkLEmSyfobY16JNH4poL9oeeEvE 

 HU1tejUtt7AZYrC9SAuqCW9MpuSqsdoedHSb1XUKjUPN 

 24ZbKS36rkPv14Tdx8qv4NRyqatTaJ5KgJrT1LxBKn5d 

 3oRPcFaRHvv9pPR6nRasigVDkm3k9kTjdfjxUpgLV5Pq 

```

```

 This seemed suspicious. Perhaps it had something to do with the stable swap math?

 It was also weird how we could only ever get at most one extra token. As usual, the best way to answer such questions is to read the code. We dived into the stable swap Solana implementation to look for a possible root cause:

 stable.rs 
```

```
 1

 // Solve for y by approximating: y**2 + b*y = c 

 2

 let mut y = d_val ; 

 3

 for _ in 0 .. ITERATIONS { 

 4

 let ( y_new , _ ) = ( checked_u8_power (& y , 2 )?. checked_add ( c )?) 

 5

 . checked_ceil_div ( checked_u8_mul (& y , 2 )?. checked_add ( b )?. checked_sub ( d_val )?)?; 

 6

 if y_new == y { 

 7

 break ; 

 8

 } else { 

 9

 y = y_new ; 

 10

 } 

 11

 } 

```

```

 approximate . Looks suspicious. Perhaps we really did find a bug in the Solana Program Library?

 With this promising find in mind, we decided to throw together a quick proof of concept. To do this, we attempted to swap very small amounts of tokens back and forth between sBTC and renBTC:

```

```
 1

 // from sbtc to renbtc 

 2

 for i in 0 .. 50 u8 { 

 3

 // create swap transaction 

 4

 let mut swap_instruction = swap ( 

 5

 & spl_token :: id (), 

 6

 & swap_pubkey , 

 7

 & swap_authority_pubkey , 

 8

 & test_account_signer . pubkey (), 

 9

 & sbtc_user_account , 

 10

 & sbtc_reserve , 

 11

 & renbtc_reserve , 

 12

 & renbtc_user_account , 

 13

 & admin_fee_account_sbtc_to_ren , 

 14

 1 , 

 15

 2 

 16

 ). unwrap (); 

 17

 18

 // nonce 

 19

 swap_instruction . data . append (& mut vec! [ i , extranonce ]); 

 20

 21

 let mut instructions = vec! []; 

 22

 23

 instructions . push ( swap_instruction ); 

 24

 25

 env . execute_as_transaction (& instructions , & vec! [& test_account_signer ]); 

 26

 } 

```

```

 It works!

 holy shit
yea, this is big

## Exploitability 

 Off-by-one bugs are much easier to exploit on Solana compared to other chains, enabled by the relatively low fees on Solana.

 A single swap on Ethereum can cost dozens of dollars, but on Solana packing hundreds of swap instructions into a single transaction costs the same flat rate of 5000 lamports. 1 

 This transaction cost discrepancy can trip up developers who transitioned from Ethereum to Solana. For example, the developers who wrote tests for the Solana Program Library implementation of stable swap assumed the impact of an off-by-one error would be negligible:

 As we mentioned previously, due to the rounding error, each swap allowed an attacker to steal a single token. Itâs important to keep in mind that this represents a single token per instruction . Transactions on Solana can also contain multiple instructions.

 With an onchain program, we are able to fit over 50 swap instructions per transaction. Each transaction can be run around 3 times before exceeding the per-instruction compute limit cap. Thus, we can pack around 150 invocations per transaction.

 Some quick napkin math confirms that this is indeed profitable. At a price of $41440 per Bitcoin, we are able to steal around 6 cents per transaction:

 10 â 8 Â BTC Ã $ 41 , 400 / BTC Ã 150 Â swaps = $ 0.0621 10^{-8}\text{ BTC} \times \$41,400/\text{BTC} \times 150 \text{ swaps} = \$0.0621 1 0 â 8 Â BTC Ã $41 , 400/ BTC Ã 150 Â swaps = $0.0621 

 At 200 transactions per second, we can extract just over a million dollars per day.

 Weâre well on our way to becoming a millionaire!

## Patch 

 Now that we had a proof-of-concept going, it was time to contact the relevant teams.

 By grepping through Solana logs for the swap instruction log, we were able to identify many potential spl-token-swap forks:

 Terminal window 
```

```
 solana logs -um | grep 'Instruction: Swap' -B1 

```

```

 With some Google dorking, we were able to identify many of these programs:

```

```
 1SoLTvbiicqXZ3MJmnTL2WYXKLYpuxwHpa4yYrVQaMZ - "1 SOL" 

 9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP - Orca Swap Program v2 

 SCHAtsf8mbjyjiv4LkhLKutTf6JnZAbdJKFkXQNMFHZ - "Sencha Swap" 

 SSwapUtytfBdBn1b9NUGG6foMVPtcWgpRU32HToDUZr - "Saros Swap" 

 SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nZg1UZ - Saber Stable Swap Program 

 SSwpMgqNDsyV7mAgN9ady4bDVu5ySjmmXejXvy2vLt1 - Step Finance Swap Program 

 SwaPpA9LAaLfeLi3a68M4DjnLqgtticKg6CnyNwgAC8 - Swap Program 

```

```

 Now it was time to contact these teams.

 Of these protocols, Saber was the only one which had BTC stable swaps, which would make exploitation immediately profitable. Luckily, they were also the most responsive, triaging and patching the vulnerability in just over one day.

 After some discussion, they decided to port a patch from Curve.fi, subtracting one from the output amount:

```

```
 1

 let dy = swap_destination_amount . checked_sub ( y )?; 

 2

 // https://github.com/curvefi/curve-contract/blob/b0bbf77f8f93c9c5f4e415bce9cd71f0cdee960e/contracts/pool-templates/base/SwapTemplateBase.vy#L466 

 3

 let dy = swap_destination_amount . checked_sub ( y )?. checked_sub ( 1 )?; 

```

```

 For reference, here is the Curve.fi implementation :

 SwapTemplateBase.vy 
```

```
 dy : uint256 = xp [ j ] - y - 1 # -1 just in case there were some rounding errors 

 dy_fee : uint256 = dy * self . fee / FEE_DENOMINATOR 

```

```

 We originally thought this was an additional patch that didnât get ported over to Solana. However, it turns out this code was actually included in the original commit , not as an additional security patch:

```

```
 commit 0fd801df7488d89f0e2fc81e760942d7858b01d6 

 Author: Ben Hauser <ben@hauser.id> 

 Date: Mon Aug 31 02:35:30 2020 +0300 

 feat: add base pool without lending 

```

```

 Date: Mon Aug 31 02:35:30 2020 +0300 feat: add base pool without lending"> 

 The commit adding stable swaps to SPL was made a few months later , meaning there was some disconnect when porting the code. Either the rounding was thought to be unnecessary, or it was simply forgotten:

```

```
 commit d62ddd2b94d5d2daaa97460b165d288610a87623 

 Author: Yuriy Savchenko <yuriy.savchenko@gmail.com> 

 Date: Tue Nov 17 15:13:18 2020 +0200 

 Added stable curve invariant to the token swap smart contract (#838) 

 * Added stable curve invariant to the token swap smart contract 

 * Fixed formatting 

 * Added missing stable curve constraints 

 * Symbol renames to make math clearer 

 * Small refactoring according to PR comments, fixes for JS tests 

```

```

 Date: Tue Nov 17 15:13:18 2020 +0200 Added stable curve invariant to the token swap smart contract (#838) * Added stable curve invariant to the token swap smart contract * Fixed formatting * Added missing stable curve constraints * Symbol renames to make math clearer * Small refactoring according to PR comments, fixes for JS tests"> 

 After contacting some other swap projects which were unaffected, we decided to notify the Solana team in order to get a patch upstreamed to the Solana Program Library .

 While few projects deploy the swap program from the Solana Program Library, the SPL program is meant as a reference implementation, and many exchanges fork their own code off of it.

 @joncinque helped triage this patch. We also asked him for his thoughts on a more complete solution:

 Honestly, the idea of just subtracting 1 from the output will cover almost all situations correctly, so itâs a good quick solution. Iâll take a look to see if we can solve this for all situations through a correct application of checked_ceil_div, as with the constant product curve.

 After some thought, he helped introduce a PR which ceilings the computation in 
```
 compute_new_destination_amount () 
```
 to correctly round within the stable curve math library:

 stable.rs 
```

```
 1

 // Solve for y by approximating: y**2 + b*y = c 

 2

 let mut y_prev : U256 ; 

 3

 let mut y = d_val ; 

 4

 for _ in 0 .. ITERATIONS { 

 5

 y_prev = y ; 

 6

 y = ( checked_u8_power (& y , 2 )?. checked_add ( c )?) 

 7

 . checked_div ( checked_u8_mul (& y , 2 )?. checked_add ( b )?. checked_sub ( d_val )?)?; 

 8

 if y == y_prev { 

 9

 let ( y_new , _ ) = ( checked_u8_power (& y , 2 )?. checked_add ( c )?) 

 10

 . checked_ceil_div ( checked_u8_mul (& y , 2 )?. checked_add ( b )?. checked_sub ( d_val )?)?; 

 11

 if y_new == y { 

 12

 break ; 

 13

 } else { 

 14

 y = y_new ; 

 15

 } 

```

```

## Closing thoughts 

 This is a good example of how messing around and interacting with the ecosystem can lead to unexpected bugs. We found this, not as a result of active security research, but as part of our work in MEV and trading.

 Another interesting takeaway is that fuzzing can give a false sense of security . Prior to our report, Saber had already deployed comprehensive fuzzers for their swap implementation. A researcher looking at code coverage alone might come to the incorrect conclusion that such extensively fuzzed code couldnât possibly have a vulnerability.

 One can see parallels to traditional security, as with Google Project Zeroâs post-mortem of the NSS overflow :

 A heavily fuzzed method had a trivial buffer overflow due to an arbitrary size limit on the input data. Implicit assumptions can often undermine security.

 Especially with regard to onchain programs, itâs important to consider what actually is a âvulnerabilityâ. Getting tokens from nothing is a more obvious example, but more subtle bugs can arise with increasingly complex DeFi interactions. Economic invariants are much harder to detect than say, memory corruption.

 A comprehensive evaluation of smart contracts relies on a deep understanding of economic implications within the Solana ecosystem.

## Footnotes 

- 
 At least prior to the 1.9 per-transaction size compute limit update. â©

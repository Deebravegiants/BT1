# [C] Phemex exploit: When your hot wallets become dozens of points of failure, $73.54 million makes for an expensive lesson in access control

## Summary
Severity: Critical
Target: Phemex
Loss: $73,540,297
Published: 01/23/2025
Source: https://rekt.news/phemex-rekt
Type: rekt-postmortem

## Details
## Phemex - Rekt

 Friday, January 24, 2025 Phemex - Rekt - CEX 

 read this article also in : 

 When your hot wallets become dozens of points of failure, $73.54 million makes for an expensive lesson in access control. 

 Phemex exchange just learned this lesson the hard way, watching helplessly as an attacker drained their hot wallets across almost 30 different chains in a masterclass of multi-chain mayhem. 

 From Solana to Ethereum, Base to Avalanche, no chain was safe as the attacker systematically emptied wallets faster than Phemex could say "access control."

 The largest centralized exchange hack of 2025 unfolded like a game of blockchain whack-a-mole - as soon as Phemex spotted suspicious activity on one chain, another wallet was already being drained.

 Their cold wallets may have stayed safe in cold storage, but their hot wallets just got a $73.54 million lesson in thermodynamics. 

 When dozens of chains share the same security flaws, does multi-chain really mean multi-risk? 

 Credit: Peckshield , Cyvers , Federico Variola , Phemex , Crypto Ady , Hacken , The Block , Tayvano 
 Almost 30 chains, one vulnerability, zero time to react - watching Phemex's hot wallets get drained was like witnessing a synchronized swimming routine choreographed by hackers. 

 PeckShield rang the first alarm bell early on January 23rd, spotting suspicious outflows that would make a bank robber blush.

 Within minutes, Cyvers' systems were lighting up like a Christmas tree, detecting over $29 million in suspicious transfers across multiple chains, but this was just the preview.

 The protocol's response followed the familiar centralized exchange playbook - suspend withdrawals first, ask questions later.

 Early security analysis by Hacken points to an access control breach that handed the attacker complete control over Phemex's hot wallets.

 Like a digital tsunami, the attack swept through blockchain after blockchain, carving out wallets in its wake. 

 Ethereum bore the heaviest blow at $17.45M, while Solana wasn't far behind, losing $14.54M. 

 XRP rounded out the podium finishes with $11.4M vanishing faster than a trader's leverage.

 The attacker carved through Bitcoin ($5.07M), BSC ($2.88M), Sui ($2457M), and Base ($2.42M).

 The rampage continued through Tron ($1.64M), Litecoin ($703k), Avalanche ($810k), and Arbitrum ($835k), while Polkadot ($758K), XLM ($863K), Polygon ($507K), Optimism ($421K), and ZkSync Era ($235K) provided the spare change.

 When you lose control access across twelve chains, you don't just misplace over $73.54 million - you write yourself into the history books of how not to handle private key management.

 This is going to be a cute post-mortem. 

 Here's how over $73.54 million evaporated chain by chain... 

## Ethereum

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0x5B34414e95a8b8D0B16a39BAf5b97CEc1d517E22 

 Stolen funds sent to: 
 0x140dEA3B704D724ddfF41597b35A10Ce0189661f 

 Amount: $17,449,663

 Time of theft: 
1/23/2025 11:49 AM UTC

## Solana

 Phemex Hot Wallet: EWSHJzKpzjpwz9GuNKkXWMHXAiwtB7obSGhdFKu5QZku 

 Attacker's Address: 3q38w9HpZcVGrKp43WSJa6KQpEfSDSoAyaebuARwbU8B 

 Stolen funds sent to: 
 CSERJWB57xayQte4xyngoUVPDcWwJgXX9V4NjPS19F66 

 Amount: $14,542,375

 Time of theft: 
1/23/2025 11:48 AM UTC

## XRP

 Phemex Hot Wallet: 
 rQKKvBvEfXbTThkqrtqaY3sAKuW6iqcMzX 

 Attacker's Address: 
 rGSu6JJ9dLZ3mpfGhtFczNjZjgoHEJcHgf 

 Amount: $11,438,331

 Time of theft: 
1/23/2025, 11:49 AM UTC

## BTC

 Phemex Hot Wallet: 
 bc1q32sxnq5hecdurfzgzp5x0zh8du86v9x84wdqdx 

 Attacker's Address: 
 bc1q7v5se5aq37g3lw8ccgre2laktpt6qrjvxqcz4p 

 Amount: $5,068,305

 Time of theft: 
1/23/25 12:02 PM UTC

## BSC

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0x6C42F03d730b7643939fA1D00416cB2985eD9cF3 

 Stolen funds sent to: 0xd760CC6F2D41E43309912D54a0955dbC8A77890f 

 Amount: $2,880,371

 Time of theft: 
1/23/2025 11:52 AM UTC

## Sui

 Phemex Hot Wallet: 0x51fc8f63faf7b22d401623f9c3ae5183e564d701741770f12ad1851c6c45a0c8 

 Attacker's Address: 
 0x4eff816c3fe9bd163d223546ef60020f0162ab4206339a0f14bdb60b639f0794 

 Stolen funds sent to: 
 0xcfcefe62850aabe2c2ed2f22078ad092e1f79575f42b997dee5d161dfb21ea9c 

 Amount: $2,452,725

 Time of theft: 
1/23/2025 12:22 PM UTC

## Base

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0x392d99Ec0348172C046cd64b85C21Df0927ab946 

 Stolen Funds sent to multiple locations: 
 Tracked on Metasleuth 

 Amount: $2.42M

 Time of theft: 
1/23/2025 11:52 AM UTC

## Tron

 Phemex Hot Wallet: 
 THAABzWrhp84Nr7gxss7qhtzA5mp3d1qUo 

 Attacker's Address: 
 TBz3DH6GUpg4cEGrcKzs8gSTvLQCGaYk5F 

 Stolen funds sent to: 
 TLz7tV8B4hAwYZ54ES1HQfRrdi8SFfxbA1 

 Amount: $1,644,321

 Time of theft: 
1/23/2025 11:48 AM UTC

## LTC

 Phemex Hot Wallet: 
 ltc1qqxaw8550zsyurqe6p8v9lyn3t883x27u7q4m89 

 Attacker's Address: 
 LU6ddXsXxwmojJkU29wu5AS67tpD3GQiXc 

 Amount: $1,052,443

 Time of theft: 
1/23/2025 - 12:05 PM UTC

## Avalanche

 Phemex Hot Wallet: 

 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0x17BCC630B1409637D42dFb278f8E2ea9fc862631 

 Stolen funds sent to: 
 0x7288CA84AB40Be3435dd33D0ceaC57Fe75eccD1D 

 Amount: $810,900

 Time of theft: 
1/23/2025 12:01 PM UTC

## Arbitrum

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0x069987773b3DeE7AC4afFb9f06A4a90f9984AB10 

 Stolen funds sent to: 
 0xAE2F4172f3665c0AA332e871B32314D26D47f465 

 Amount: $835,373

 Time of theft: 
1/23/2025 11:59 AM UTC

## Polkadot

 Phemex Hot Wallet: 
 15hTaSogYFyGyRJhXdpQWRR1J9oya5nj4nFppi4XgUVMCvmP 

 Attacker's Address: 
 1xjLtr1PTVi4hkSkG81HEf4mVpq9FRyEAQunGiBjQJ2VvLq 

 Stolen funds sent to: 
 139PZAjWoAHxjh6gAzrqnoQN9bniSELHXh3xzabXqho6eciP 

 Amount: $758,712

 Time of theft: 
1/23/2025 12:41 PM UTC

## XLM

 Phemex Hot Wallet: 
 GDPKBXKNPZYU3TH2WCM7DFA2LBX76MJMRYT6BAIO7ZL6KYD2WVBXCYE6 

 Attacker's Address: 
 GCX7AQYXMNNDC4YRR4MPMSJ23KU7ZJ3EOBS2QJDPALQHJDJGYRTFK432 

 Amount: $703,098

 Time of theft: 
1/23/2025 12:48 PM UTC

## Polygon

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0xf493033B14cE39CBC6a283921eA50919C5D43Dfe 

 Stolen funds sent to: 
 0xc590175E458b83680867AFD273527Ff58f74c02b 

 Stolen Funds also sent here: 
 0x9B52594bFe50c51A75a8775ea03aD687E25E6A58 

 Amount: $507,725

 Time of theft: 
1/23/2025 12:05 PM UTC

## Optimism

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0xE9AA4a999ca1D9093054CF4f5dc221a06D433650 

 Stolen Funds sent to multiple locations: 
 Tracked on Metasleuth 

 Amount: $421,575

 Time of theft: 
1/23/2025 12:48 PM UTC

## ZkSync Era

 Phemex Hot Wallet: 
 0x50be13b54f3eebbe415d20250598d81280e56772 

 Attacker's Address: 
 0xEba89b66C132E7fAd2a238BF416Fb9d45dcAd1FF 

 Stolen funds sent to: 
 0xB66aF6Fe0478507f2cF74F43a2bc383fdcF8d09c 

 Amount: $235,176

 Time of theft: 
1/23/2025 12:41 PM UTC

 But wait, there’s more. The ever vigilant blockchain sleuth, Tayvano, highlighted the theft was worse than initially thought . 

 Stolen funds tracked since initial story… 

## DOGE

 Phemex Hot Wallet: 
 DDF87yUT8FLEXDuRi4BpVn2rNcvQjdR8JC 

 Attacker's Address: 
 DHomi9Nx7K5tG8A3afBJrSq6PxKuGAeHGZ 

 Stolen funds sent to: 
 DCvPsn3KQzJzgJ5yfnMqrXkfLnWv5Mvi5F 

 Amount: $3,633,968

 Time of theft: 
1/23/2025 12:15 PM UTC

## ADA

 Phemex Hot Wallet: 
 addr1v8hhy20gp9fm0769ajlzg5untmfddqy9ak5u5nytr2xtguchjnwp0 

 Attacker's Address: 
 addr1q8st8zg9ynw995zqtlrfuajw6vua49m9depzzf8ed7zah3hqkwys2fxu2tgyqh7xnemya5eem2tk2mjzyyj0jmu9m0rqtwuq0c 

 Stolen funds sent to: 
 addr1qy3ve3s6lt7pvc3wr86wsthnzu5ft6ftkqvf6yzx2ljy9typnu46f24lu30ht9zws8r4w7587r6q6k7v6426kzvt6qfqyf65ml 

 Amount: $1,965,385

 Time of theft: 
1/23/2025 11:51 AM UTC

## HEDERA

 Phemex Hot Wallet: 
 0.0.5791784 

 Attacker's Address: 
 0.0.8154399 

 Stolen funds sent to: 
 0.0.8163960 

 Amount: $2,073,385

 Time of theft: 
1/23/2025 12:01 PM UTC

## ALGO

 Phemex Hot Wallet: 
 GVDYDJGOJRRUPDNTUOIZ7CNTMRMC33LY2ULRQBWBTSJSURXHEXIJHO5NHU 

 Attacker's Address: 
 PU4WSJFPJF6E33LZ5FECO3I3GTYPB6Z3NBGNW7ERZGMPVEPFQW4E2YMRFU 

 Amount : $874,161

 Time of theft: 
1/23/2025 11:49 AM UTC

## TON

 Phemex Hot Wallet: 
 UQBMwzh34D70qj_nEzB2jkX_hdRhEI68LJSa6pww7eQmBBRB 

 Attacker's Address: 
 UQCwH0gq9fOGklHDC5Dr8VY9_YgBe_-AJvhxbqAtyxoUJaQi 

 Amount: $518,278

 Time of theft: 
1/24/2025, 06:49 PM UTC

## FILECOIN

 Phemex Hot Wallet: 
 f16o24ornzrfuhdpivbcm43fzem2uum35ycp7dlyy 

 Attacker's Address: 
 f1ewajq4cw3rjzzpvwkkrnn3j7xlvuece4t5ez37q 

 Amount: $332,764

 Time of theft: 
1/23/2025 07:40 AM UTC

## XDC

 Phemex Hot Wallet: 
 0x50BE13b54f3EeBBe415d20250598D81280e56772 

 Attacker's Address: 
 0x521ca0920fe5f77c63cb4e6aa9567a0c460c1b26 

 Amount: $310,393

 Time of theft: 
1/23/2025 12:59 PM UTC

## ZCASH

 Phemex Hot Wallet: 
 t1c8KB1JCzp7duNdtedEDjNTPSCSn24h6Mz 

 Attacker's Address: 
 t1fhmRhP1HrD8PnSUzpCK578YGLfh9Gms4L 

 Amount: $130,603

 Time of theft: 
1/23/2025 15:43 PM UTC

## COSMOS

 Phemex Hot Wallet: 
 cosmos1vfq5qfnefwpsarsqnlas9894rrm5rm095xm99z 

 Attacker's Address: 
 cosmos1sr7lxvfm0a2pfjv8gt7jy6df2k7jyas6jl2ksq 

 Amount: $129,887

 Time of theft: 
1/23/2025, 15:11 PM UTC

## ETC

 Phemex Hot Wallet: 
 0x42984Ce6bA186Fd684C92ed3165fa029BE2F217E 

 Attacker's Address: 
 0x4919d3793e1d4FFEa2b824B7A579414533950b00 

 Stolen Funds sent to: 
 0xd30dc7fb42a7054cbe8b140bd038498e9ba562eb 

 Amount: $104,969

 Time of theft: 
1/23/2025 10:03 AM UTC

## BCH

 Phemex Hot Wallet: 
 qr057zsy6xhn5puu7kymhu80ka0tz2lha58djpdpap 

 Attacker's Address: 
 qpj5y07s0789cganpajx8pkx28vr93alecnmrwszlv 

 Stolen Funds sent to: 
 qz62nkswtf5v0kytwujajq6pw98pymqxssnht3r50f 

 Amount: $92,670

 Time of theft: 
1/23/2025 17:11 PM UTC

## TEZOS

 Phemex Hot Wallet: 
 tz1Rwf9herudqoEDSYXDCT4Urf9iEhE6uX92 

 Attacker's Address: 
 tz1NWRQ8Ps369H1E28J5A67HEWcgVRkFTYfn 

 Stolen Funds sent to: 
 tz1WyPed25WRdessWkVSDkuJgivcu3E12ndL 

 Amount: $101,093

 Time of theft: 
1/23/2025 10:10 AM UTC

## DASH

 Phemex Hot Wallet: 
 Xw1TakcVnYXjQsi2fJgo8QRt4UcVfMXPQM 

 Attacker's Address: 
 XoQYiJUY81E1YUGtuQFFsESzVfwqxi12od 

 Stolen Funds sent to: 
 XnH1LZugZHhqMn3JgLjM7mJwVScyTmArnh 

 Amount: $51,648

 Time of theft: 
1/23/2025 11:40 AM UTC

 Total Stolen (adjusted for 2/3/2025): $73,540,297

 As the funds trickled across blockchains , it became clear that Phemex's sprawling multi-chain approach may have been more of a bug rather than a feature. 

 The clinical precision of the attack revealed more than just stolen funds - it exposed the fatal flaw in Phemex's multi-chain ambitions. 

 As MetaMask's principal security researcher Taylor Monahan told The Block the sophistication of the attack - simultaneous drains across chains, methodical token swapping prioritizing freezable assets, and manual execution instead of scripted chaos.

 While Phemex rushed to reassure users about their cold wallet security, they forgot the first rule of hot wallet management - if you can't secure one chain, maybe don't try securing over a dozen.

 The team quickly promised a compensation plan would be "announced soon," as if throwing money at the problem could patch their security holes.

 They might need a bigger compensation fund if they keep treating multi-chain security like a game of whack-a-mole. 

 When every chain becomes a potential point of failure, is multi-chain support really a feature - or just over a dozen ways to get rekt? 

 Whether through leaked private keys or compromised access controls, exchange security keeps failing with clockwork precision. 

 Multi-chain support sounds fantastic until dozens of different doors swing open simultaneously, inviting thieves to a $73.54 million shopping spree. 

 Phemex's hot wallet massacre joins an increasingly crowded club of exchanges who've learned that wallet security isn't just a suggestion - it's an expensive lesson in the art of losing control.

 Time will tell if we discover the full story behind this exploit. 

 Though if history is any guide, the root cause of access control and private key breaches has a tendency to remain mysteriously classified. 

 In other words, we don’t always find out the entire story.

 The details fade but the pattern remains crystal clear

 Hot wallet permissions keep failing, transparency remains optional, and exchanges keep pretending they're ready for multi-chain custody. 

 Which chain will leak next - or have exchanges finally mastered the art of losing money across all of them? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

# [H] Raydium exploit: The latest entry on our leaderboard comes from a post-FTX wasteland, once a promising hive of VC-backed dev activity

## Summary
Severity: High
Target: Raydium
Loss: $4,400,000
Published: 12/16/2022
Source: https://rekt.news/raydium-rekt
Type: rekt-postmortem

## Details
## Raydium - REKT

 Monday, December 19, 2022 Raydium - Solana - REKT 

 read this article also in : zh 

 The latest entry on our leaderboard comes from a post-FTX wasteland, once a promising hive of VC-backed dev activity. 

 On Friday, Raydium , a Solana-based AMM, lost a total of ~$4.4M in fees from its liquidity pools. 

 The alarm was raised by the DEX aggregator PRISM, also on Solana:

 There seems to be a wallet is draining LP Pools from Raydium liquidity pools using admin wallet as a signer without having/burning LP tokens.

 We withdrew protocol provided PRISM/USDC liquidity from Raydium

 WITHDRAW YOUR PRISM/USDC LIQUIDITY FROM RAYDIUM

 The official announcement came 40 minutes later, stating that “ authority has been halted on AMM & farm programs for now ”. In a follow-up post , the team assured users that “ a patch is in place preventing further exploits from the attacker. ”

 While this incident doesn’t look to have caused a total protocol meltdown, losing millions is never a good look.

 But who’s still using Solana anyway? 

 Credit: Raydium , OtterSec 

 According to OtterSec, the incident appears to have been down to a compromised private key to the owner account of Raydium contracts. 

 Raydium suspect “ a trojan attack and compromised private key for the pool owner account ”.

 The account had authority over certain functions of Raydium’s pools, allowing the attacker to drain accumulated trading/protocol fees via the withdraw_pnl instruction. The hacker also changed the SyncNeedTake parameter to increase expected fees and withdraw extra funds.

 The following pools were affected for a total protocol loss of $4.4M: 

 SOL-USDC

 SOL-USDT

 RAY-USDC

 RAY-USDT

 RAY-SOL

 stSOL-USDC

 ZBC-USDC

 UXP-USDC

 whETH-USDC

 The majority of funds were bridged to Ethereum, swapped to ETH and have been deposited into Tornado Cash. 100k SOL ($1.4M) remains in the attacker’s Solana address.

 Attacker’s SOL address AgJddDJLt17nHyXDCpyGELxwsZZQPqfUsuwzoiqVGJwD 

 Attacker’s ETH address 0x7047912c295cd54d6617b5d0d6d8b324a11c91db 

 As ever with cases of “compromised keys” we must ask ourselves if this could simply have been an insider looking for a bit on the side.

 The bear market promises a long, tough road ahead for many smaller teams, especially in this context...

 The future of Solana feels uncertain. 

 Following the collapse of FTX and downfall of the now-imprisoned SBF with whom the ecosystem was so closely associated, it’s easy to see how an ecosystem dev might be sick from the fallout and be tempted to take the easy way out.

 As with so many of the cases we’ve covered, we’ll likely never know. 

 Who’s next? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

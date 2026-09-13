# [C] Transit Swap exploit: Sunday morning notifications of a cross-chain protocol losing millions

## Summary
Severity: Critical
Target: Transit Swap
Loss: $21,200,000
Published: 10/02/2022
Source: https://rekt.news/transit-swap-rekt
Type: rekt-postmortem

## Details
## Transit Swap - REKT

 Sunday, October 2, 2022 Transit Swap - REKT 

 read this article also in : zh 

 Working on the weekend like usual… 

 Sunday morning notifications of a cross-chain protocol losing millions.

 Just like the good old days.

 Transit Swap has lost $21M to a vulnerability which allowed an unknown attacker to drain the wallets of users who had approved the protocol's swap contracts. 

 But unfortunately for the hacker, over $1M was lost in transit … not all MEV bots are down 0xbad this week. 

 The team paused the affected contracts before announcing the incident on Twitter.

 Then came an update that via “ the joint efforts of the @SlowMist_Team , the @Bitrace_Team , the @peckshield security team, ” key info about the hacker, including their “ IP, email address, and associated on-chain addresses ” had been uncovered.

 As the attacker’s anonymity began to slip away, it seems they had second thoughts. So far, over 70% of the funds have been returned.

 Finding a vulnerability in an unverified contract; diligent decompiler, or someone acting on insider info? 

 Though the vulnerability was in the project’s code, this attack targeted the users directly via a vulnerability in the use of the transferFrom() function. Any tokens approved for trading on Transit Swap could be transferred directly from users’ wallets to the unknown exploiter’s address. 

 The first attack tx occurred just after 18:30 UTC, with the attack lasting approximately half an hour before swapping stolen tokens to ETH and BNB.

 Exploiter’s address on ETH and BSC : 0x75f2aba6a44580d7be2c4e42885d4a1917bffd46

 Vulnerable contract (revoke approvals on both ETH and BSC): 0xed1afc8c4604958c2f38a3408fa63b32e737c428

 Credit: Supremacy Inc. , SlowMist 

 The project’s smart contracts are unverified. However, they can be decompiled from the published bytecode:

 After understanding the hacker's attack path, we tried to find out the cause of the vulnerability, but the smart contracts of the project are closed-source contracts. So we decompiled it and finally found the root cause of this attack: a controllable transferFrom external call

 Because it is decompiled code, it is a little obscure for readers to understand. We can understand that varg0 is the token address, varg1, varg2 and varg3 are the from, to and amount parameters of the transferFrom function.

 0x23b872dd in the figure is transferFrom() function signature of the function. Therefore, the claimTokens function calls the transferFrom function of an address, and the address and function parameters are controllable.

 For a more detailed explanation, see SlowMist’s analysis . 

 Peckshield also provided a visual summary of the attacker’s activities.

 The returned funds have been consolidated into the same address (0xD989f7B4320c6e69ceA3d914444c19AB67D3a35E) on ETH and BSC , which holds a total of ~$16.5M across the two chains.

 Stolen funds: 

- 3180 ETH ($4.2M), returned .

- 1500 Binance-pegged ETH ($2M), returned .

- 50k BNB ($14M), $10.4M returned .

 At the time of writing, the exploiter’s BSC address still holds over $3.5M in stolen BNB and previously sent 2500 BNB ($715k) to Tornado Cash. 

 The fast response and cooperation between multiple security teams meant this incident had a happier ending than most.

 But a protocol using live, unverified contracts is never a good look in DeFi, where open-source is the name of the game. 

 Hiding contract code makes DYOR all but impossible, and impedes the work of whitehats to spot vulnerabilities before they’re exploited.

 Closed-source code also breeds suspicion in the blockchain world, where exploits, rug-pulls and “compromised keys” are often forgotten within weeks. 

 Could this be a case of an insider using privileged info against their users, before returning most of the funds and hoping it will all blow over? 

 Business as usual. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

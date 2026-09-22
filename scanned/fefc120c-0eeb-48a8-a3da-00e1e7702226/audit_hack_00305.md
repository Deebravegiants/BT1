# [C] XToken exploit: A sub-species of crypto users have developed superhuman abilities which allow them to tear through holes in smart contracts or mould them to their wil

## Summary
Severity: Critical
Target: XToken
Loss: $24,000,000
Published: 05/12/2021
Source: https://rekt.news/xtoken-rekt
Type: rekt-postmortem

## Details
## XToken - REKT

 Wednesday, May 12, 2021 XToken - REKT 

 read this article also in : zh 

 The X-ploiters live amongst us. 

 A sub-species of crypto users have developed superhuman abilities which allow them to tear through holes in smart contracts or mould them to their will with flash loans and arbitrage.

 Nobody is entirely safe from the anonymous team. 

 However, rekt.news is here to help by archiving the stories of the infamous X-ploiters so that our readers can learn and future generations may be protected from their brutal attacks.

 This was no cheap ticket - XToken is a quality protocol with strong partnerships. Hacks like these remind us that even the “blue chips” aren’t entirely safe.

 What went wrong? 

 Credit: 0xdeadfce & Frankresearcher 

 Exploit Transaction 

 xToken.Market, a decentralized passive investing protocol, was exploited with the use of flash loans. 

 Over $24 million was taken from the yield-bearing liquidity pools for SNX (xSNXa) and BNT (xBNTa). 

 At 15:14 UTC X-Token released the following warning .

 Minting on all contracts has been paused as we investigate reports.

 The community alerted us to X-Tokens tweet within minutes.

 A second tweet explained that:

 xSNXa and xBNTa contracts have been exploited. Minting paused on all contracts as we investigate further.

 Liquidity pools have been drained, however most SNX and BNT remain in xToken contracts.

 The attacker used a Flashloan from DyDx for 61,833 ETH (~$267M) and a Private Transaction using Flashbots MEV to facilitate the attack.

 Funds lost 

- 2.4k ETH ($10.3M)

- 781k BNT ($6.2M)

- 407k SNX ($8M)

- 1.9B xBNTa

 All tokens except xBNTa have already been sold to ~5.6k ETH through 1inch. 

 1: Hacker borrowed 61.8k ETH flash loan on dYdX

 2: Deposited 10k ETH to borrow 564k SNX on Aave and swap 5.5k ETH to 700k SNX on SushiSwap

 3: Sold 1.2M SNX for 818 ETH on Uniswap v2, significantly reducing the SNX price.

 4: Used only 0.12 ETH to mint 1.2B xSNXa, because the protocol buys SNX through Kyber, who in turn led to use Uniswap v2 for this swap.

 5: However, within the protocol, xSNXa price turned out to be normal, which made it possible to swap 105M xSNX into 414 ETH.

 6: After that, the attacker began to do reverse swaps in SushiSwap and Uniswap and repaid loans in Aave.

 7: Then they also began to sell the existing xSNXa to the Balancer SNX/ETH/xSNXa (25/25/50) pool.

 8: Repaid flash loan to dYdX.

 9: Issued xBNTa four times for 0.03 ETH, which ultimately gave them 3.9B xBNTa.

 10: Swap half of xBNTa to 781k BNT.

 Another $24 million gone, yet the only unusual thing is the names involved. 

 We’re not used to seeing our blue chip babies involved in such violence.

 Perhaps that label gives a false sense of security, even the most time-tested protocols are still incredibly new when you look long term.

 A new entry onto our leaderboard for XToken as they take the number 9 spot, but it’s the fourth time for their security auditor Peckshield, making them the most rekt auditor on the rekt.news leaderboard.

 But then again, perhaps a $24 million bounty is worth another spot on the leaderboard…

 Did this attack come from within? 

 We may never know, but we will always wonder. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.

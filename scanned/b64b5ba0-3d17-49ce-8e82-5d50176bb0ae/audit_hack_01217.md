# [H] BNBChain incident: BNBChain was attacked and lost more than 500 million US dollars. According to SlowMist, the hacker’s initial source of funds was C

## Summary
Severity: High
Target: BNBChain
Loss: 2,000,000 BNB
Attack method: Pseudo-authentication
Published: 2022-10-06
Source: https://twitter.com/SlowMist_Team/status/1578220472373649408
Type: slowmist-incident

## Details
BNBChain was attacked and lost more than 500 million US dollars. According to SlowMist, the hacker’s initial source of funds was ChangeNOW, and the hacker’s address has interacted with multiple DApps, including Multichain, Venus Protocol, Alpaca Finance, Stargate, Curve, Uniswap, Trader Joe, PancakeSwap, SushiSwap, etc. Analyst @samczsun posted a post explaining how hackers used Binance Bridge to steal BNB. The attackers stole 1 million BNB twice, but both used the height of 110217401, which is much lower than the normal height. Furthermore, the proof submitted by the attacker is shorter than the legitimate proof, showing that the attacker forged the proof for that particular block. The specific method is to add a new leaf node when the COMPUTEHASH function generates a hash, and then create a blank internal node to satisfy the prover, and exit early after finding a matching hash with the internal node. So far, only two fake verifications have been generated in this way.

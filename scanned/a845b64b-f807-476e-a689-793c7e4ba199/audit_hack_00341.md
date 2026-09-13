# [M] CashCowCoin incident: CashCowCoin’s unverified trading router implementation contract had a flawed sell() flow. After the PancakeSwap Router completed t

## Summary
Severity: Medium
Target: CashCowCoin
Loss: $ 117,400
Attack method: Smart Contract Vulnerability
Published: 2026-08-27
Source: https://x.com/SlowMist_Team/status/2093219144896557483
Type: slowmist-incident

## Details
CashCowCoin’s unverified trading router implementation contract had a flawed sell() flow. After the PancakeSwap Router completed the CCC→WBNB swap, the proxy called a privileged token function to transfer post-tax CCC from the Pair to the dead address and invoked Pair.sync(). This burned the sell-side CCC while permanently retaining the reduced WBNB reserve, enabling repeated draining of the pool’s WBNB through about 80 iterative sell cycles.

# [H] LABUBU/OLPC incident: The OLPC/LABUBU liquidity pool on PancakeSwap V2 (BNB Chain) was exploited, resulting in approximately $1.1 million in losses. The

## Summary
Severity: High
Target: LABUBU/OLPC
Loss: $ 1,100,000
Attack method: Smart Contract Vulnerability
Published: 2026-06-20
Source: https://x.com/PeckShieldAlert/status/2068314444422402515
Type: slowmist-incident

## Details
The OLPC/LABUBU liquidity pool on PancakeSwap V2 (BNB Chain) was exploited, resulting in approximately $1.1 million in losses. The attacker exploited a logic vulnerability in the OLPC token contract’s _update function. Approximately 46 days prior, the OLPC owner had maliciously changed the decimalsValue parameter to an extremely large value (7326680472586200649) and later renounced ownership. A small OLPC transfer triggered massive burns of OLPC and LABUBU tokens from the pool (to the dead address), desynchronizing the pair’s cached reserves. This allowed the attacker to drain a large amount of LABUBU, which was swapped through intermediate pools for ~1.115 million USDT. Funds were bridged to Ethereum and deposited into Tornado Cash.

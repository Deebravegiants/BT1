# [M] FH Token incident: FH Token on the BSC chain was exploited in its FH/USDT liquidity pool on PancakeSwap V2. A flaw in the token’s _transfer function

## Summary
Severity: Medium
Target: FH Token
Loss: $ 20,000
Attack method: Smart Contract Vulnerability
Published: 2026-08-26
Source: https://x.com/TenArmorAlert/status/2092427353456812207
Type: slowmist-incident

## Details
FH Token on the BSC chain was exploited in its FH/USDT liquidity pool on PancakeSwap V2. A flaw in the token’s _transfer function and isSell logic caused incorrect token burns during sells, allowing the attacker to drain funds from the pool through repeated buy-and-sell loops, resulting in a loss of approximately $20,000.

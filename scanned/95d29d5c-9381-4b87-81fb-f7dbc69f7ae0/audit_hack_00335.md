# [M] Float Protocol incident: An attacker used a flash loan to execute large swaps on a Uniswap V3 pool and manipulate the spot price (slot0). This caused Float

## Summary
Severity: Medium
Target: Float Protocol
Loss: $ 28,000
Attack method: Flash Loan Price Manipulation
Published: 2026-08-31
Source: https://x.com/SlowMist_Team/status/2094373942291026287
Type: slowmist-incident

## Details
An attacker used a flash loan to execute large swaps on a Uniswap V3 pool and manipulate the spot price (slot0). This caused Float Protocol’s Hypervisor contracts to misprice LP shares. Because critical functions lacked TWAP/oracle validation and slippage protection, the attacker repeatedly deposited and withdrew at inflated share values, extracting about $28,000 (10.71 ETH).

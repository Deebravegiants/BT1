# [M] warp.green incident: The ERC-20 bridge of warp.green (a cross-chain messaging protocol between Chia and EVM chains) suffered an exploit due to a vulner

## Summary
Severity: Medium
Target: warp.green
Loss: $ 93,000
Attack method: Smart Contract Vulnerability
Published: 2026-08-23
Source: https://x.com/warpdotgreen/status/2091772015598325920
Type: slowmist-incident

## Details
The ERC-20 bridge of warp.green (a cross-chain messaging protocol between Chia and EVM chains) suffered an exploit due to a vulnerability in the Chia-side Chialisp puzzle. The attacker minted worthless CAT tokens, presented them as burned wUSDC, obtained validator signatures, and drained ~$93,000 USDC from the Base and Ethereum bridge contracts, later converting the funds to ETH. The CAT bridge (securing assets like wXCH) appears unaffected.

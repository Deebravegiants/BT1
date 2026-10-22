# [M] OMNI404 incident: Ethereum ERC-404 token OMNI404 (O404) derived NFT mint/burn counts from integer balanceOf/units diffs in _transfer(). Its transfer

## Summary
Severity: Medium
Target: OMNI404
Loss: $ 5,923
Attack method: Smart Contract Vulnerability
Published: 2026-09-11
Source: https://x.com/SlowMist_Team/status/2098300936720695573
Type: slowmist-incident

## Details
Ethereum ERC-404 token OMNI404 (O404) derived NFT mint/burn counts from integer balanceOf/units diffs in _transfer(). Its transfer() treated values ≤50 as ERC-721 IDs but still moved a fixed 1e18 units. Using flash loans and Uniswap V3 exact-output swaps (transfer(recipient, 1/2/.../21)), the attacker received full-unit tokens while the pool booked wei-level amounts, draining about 2.4 WETH.

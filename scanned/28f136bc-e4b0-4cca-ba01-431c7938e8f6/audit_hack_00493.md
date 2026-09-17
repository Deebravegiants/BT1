# [M] SAS Token incident: The SAS Token on BNB Chain was exploited via a flawed custom transfer logic (Deferred Burn Exploit). The token’s custom transfer l

## Summary
Severity: Medium
Target: SAS Token
Loss: $ 12,000
Attack method: Smart Contract Vulnerability
Published: 2026-04-02
Source: https://blocksec.com/blog/weekly-web3-security-incident-roundup-mar-30-apr-5-2026
Type: slowmist-incident

## Details
The SAS Token on BNB Chain was exploited via a flawed custom transfer logic (Deferred Burn Exploit). The token’s custom transfer logic had a flaw: sending SAS to the LP pool only incremented a global sellBurn counter, while any subsequent ordinary transfer could burn SAS directly from the pool and call sync() to rewrite reserves, bypassing the AMM’s swap logic. The attacker accumulated sellBurn credit through sells, triggered an unrelated ordinary transfer to burn SAS from the pool down to ~1 wei, and then reverse-swapped to extract profit.

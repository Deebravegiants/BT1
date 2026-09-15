# [H] Aark Digital incident: During a routine GM token burn, Aark Digital encountered a callback error due to a third-party contract modification. To resolve t

## Summary
Severity: High
Target: Aark Digital
Loss: $ 1,900,000
Attack method: Incorrect Balance Update
Published: 2024-10-25
Source: https://aarkdigital.medium.com/incident-of-october-25th-d074f32d6535
Type: slowmist-incident

## Details
During a routine GM token burn, Aark Digital encountered a callback error due to a third-party contract modification. To resolve this, Aark Digital initiated a contract upgrade and GM delisting to adjust affected user balances. Users holding GM were required to convert GM to USDC. Aark Digital ran a script to process these conversions, receiving inputs like target user, amount, token address, and decimals from event data. While executing, a single user’s USD Value shifted erroneously from 0.498942 to 498,942 * (10 ^ 12), due to an incorrect balance update (not from a deployed contract error). Exploiting this security vulnerability, the attacker caused Aark Digital a loss of 1,499,841 USDC and 159.09 ETH.

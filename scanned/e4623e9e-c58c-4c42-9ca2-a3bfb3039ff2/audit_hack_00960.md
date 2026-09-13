# [H] MEV Bot incident: The MEV Bot (0x05f016765c6c601fd05a10dba1abe21a04f924a5) was exploited and lost about 1k ETH! The core reason is that the 0xf6ebeb

## Summary
Severity: High
Target: MEV Bot
Loss: $ 2,152,392
Attack method: Flash Loan Attack
Published: 2023-11-07
Source: https://twitter.com/SlowMist_Team/status/1722081647028478029
Type: slowmist-incident

## Details
The MEV Bot (0x05f016765c6c601fd05a10dba1abe21a04f924a5) was exploited and lost about 1k ETH! The core reason is that the 0xf6ebebbb function used to trigger arbitrage in the contract lacks authentication. The attacker calls this function to exchange the tokens in the contract into the pool on curve, and then uses funds of the flash loan to reverse exchange and obtain profit.

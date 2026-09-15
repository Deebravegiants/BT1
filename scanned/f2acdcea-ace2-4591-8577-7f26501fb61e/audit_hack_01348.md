# [H] Meter.io incident: Meter.io's cross-chain bridge was hacked, resulting in a loss of around $4.3 million ( 1391.24945169 ETH and 2.74068396 BTC). The

## Summary
Severity: High
Target: Meter.io
Loss: $ 4,300,000
Attack method: Contract Vulnerability
Published: 2022-02-06
Source: https://twitter.com/Meter_IO/status/1490103308421255168
Type: slowmist-incident

## Details
Meter.io's cross-chain bridge was hacked, resulting in a loss of around $4.3 million ( 1391.24945169 ETH and 2.74068396 BTC). The hacker was able to exploit a vulnerability in the deposit function, which allowed them to fake BNB or ETH transfers. Meter.io announced that Meter Passport (a cross-chain bridge extension) automatically wraps and unwraps Gas Tokens (such as ETH and BNB) for user convenience. However, the contract did not prohibit the wrapped ERC20 Token from interacting directly with the native Gas Token, nor did it properly transfer and verify the correct amount of WETH transferred from the caller address.

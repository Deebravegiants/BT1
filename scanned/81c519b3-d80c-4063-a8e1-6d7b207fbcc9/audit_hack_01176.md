# [M] Polynomial Protocol incident: Polynomial Protocol has a loophole in optimism's deposit contract. The problem stems from the swapAndDeposit() function, which has

## Summary
Severity: Medium
Target: Polynomial Protocol
Loss: -
Attack method: Contract Vulnerability
Published: 2022-12-12
Source: https://twitter.com/0xPoor4ever/status/1602156729105788929
Type: slowmist-incident

## Details
Polynomial Protocol has a loophole in optimism's deposit contract. The problem stems from the swapAndDeposit() function, which has no restrictions on its input. Anyone can pass in an address and maliciously construct swapData to steal contract-approved tokens.

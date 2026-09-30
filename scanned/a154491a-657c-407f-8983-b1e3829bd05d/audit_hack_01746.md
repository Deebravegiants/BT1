# [M] SpankChain incident: The attacker created a malicious contract masquerading as an ERC20 token, and the "transfer" function re-invokes the payment chann

## Summary
Severity: Medium
Target: SpankChain
Loss: 165.38 ETH
Attack method: Reentrancy attack
Published: 2018-10-09
Source: http://dy.163.com/v2/article/detail/DTN9R2MA0519U3I5.html
Type: slowmist-incident

## Details
The attacker created a malicious contract masquerading as an ERC20 token, and the "transfer" function re-invokes the payment channel contract repeatedly, each time exhausting some ETH.

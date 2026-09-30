# [M] A malicious user can use block stuffing to avoid challenging his proposed transactions

## Summary
Severity: Medium
Reporter: Bitter Rose Goose
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# A malicious user can use block stuffing to avoid challenging his proposed transactions

## Summary
An user can propose a malicious transaction (a one for drain all owner balance for eg) and then use block stuffing to avoid his transaction to be challenged to be able to execute it   

## Vulnerability Detail
Block stuffing is a type of attack in blockchains where an attacker submits transactions that deliberately fill up the block’s gas limit and stall other transactions.  
It could be so that the attacker wants to stall transactions with a specific contract, in this case to avoid its transaction been challenged, to be able to execute it.  

## Impact
An user with sufficient ammount of gas can DoS transaction that attemps to block his propossed transactions  

## Code Snippet

## Tool used

Manual Review

## Recommendation
Enforce a big challenge period value to make the block stuffing non profitable for attackers

## References
https://medium.com/hackernoon/the-anatomy-of-a-block-stuffing-attack-a488698732ae

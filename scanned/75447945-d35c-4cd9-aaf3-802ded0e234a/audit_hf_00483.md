# [H] Insecure calls to safeTransfer

## Summary
Severity: High
Contest weight: 0.2968
Dataset id: 1925
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function safeTransferFrom() is used to transfer tokens from user to the protocol contract. This function is used in modifyOrder and createOrder with the recipent address as the owner form who the tokens will be transfered from. An attacker can abuse this functionnality to create unfaire orders for a protocol user that approve more tokens than needed to the protocol contract the fill the order immediatly and gain instant profit while the victim lost his tokens.
In OracleLess.sol::procureTokens():280
ntracts/automatedTrigger/OracleLess.sol#L280 procureTokens() implement tokens transfer from an owner address to the protocol contract
ob/main/oku-custom-order-types/contracts/automatedTrigger/StopLimit.sol#L171
In StopLimit.sol::modifyOrder():226-230
ntracts/automatedTrigger/StopLimit.sol#L226-L230
In Bracket.sol::modifyOrder():250-254
ntracts/automatedTrigger/Bracket.sol#L250-L254
Internal pre-conditions
External pre-conditions
1. A user should have approve more tokens than needed for a trade that whould result in some residual allowance to the protocole contract
Attack Path
1. The attacker create/modify an unfaire order with the victim as recipent with an amounIn <= residual allowance
2. The prococol then transfer the tokens from the user to create the order
3. The attacker fill the order an gain instant profit

## Recommendation
It would be better to use msg.sender to ensure that the recipient/owner of the order is the order creator or juste use msg.sender as parameter to the safeTransferFrom() function call instead of order recipient

# [M] RCFactory uberOwner cannot be burned

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/78
Type: code-finding

## Details
# Handle

0xRajeev


# Vulnerability details

## Impact

The notice for changeUberOwner() and the documentation indicates there may be a requirement to renounce the uberOwner address at some point possibly to prevent further changes to reference market contract address. This is typically done by setting it to 0 burn address. However, because of the zero-address check in changeUberOwner(), this is not possible in the current implementation.

Impact: uberOwner can never be renounced by burning to 0 address.

## Proof of Concept

https://github.com/code-423n4/2021-06-realitycards/blob/86a816abb058cc0ed9b6f5c4a8ad146f22b8034c/contracts/RCFactory.sol#L444-L449

https://github.com/code-423n4/2021-06-realitycards#mortar_board-governance-mortar_board

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/00128bd26061986d10172573ceec914a4f3b4d3c/contracts/access/Ownable.sol#L48-L58

## Tools Used

Manual Analysis

## Recommended Mitigation Steps

Create a special renounceUberOwner() function (similar to OpenZeppelin’s renounceOwnership) for specifically setting it to burn address 0 and renouncing. This will allow changing it (to a non-owner address or a multisig) using the current changeUberOwner() function but also renouncing it by burning if/when necessary.

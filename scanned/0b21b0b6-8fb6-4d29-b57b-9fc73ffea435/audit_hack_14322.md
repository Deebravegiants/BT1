# [M] `URI_SETTER` and `MINTER_ROLE` cannot be assigned to other address

## Summary
Severity: Medium
Reporter: ubermensch
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L41-L55
Type: audit-issue

## Details
# `URI_SETTER` and `MINTER_ROLE` cannot be assigned to other address

## Summary
This finding pertains to the use of the `AccessControl `contract by `OpenZeppelin `for role-based access control. The contract only uses the `_setupRole `function in the constructor for the `URI_SETTER` and `MINTER_ROLE` roles, which by default assigns the `DEFAULT_ADMIN_ROLE` to the zero address. This means that no one can assign the `URI_SETTER` and `MINTER_ROLE` to new addresses.

## Vulnerability Detail
The contract uses the `_setupRole` function to assign roles in the `constructor`. However, it does not assign the `DEFAULT_ADMIN_ROLE` to any specific address, leaving it as the zero address. This means no one can assign the `URI_SETTER` and `MINTER_ROLE` to new addresses, which is not practical especially if the initial addresses are compromised or the team would like to build new contracts that need to communicate with this one.

## Impact
If the DEFAULT_ADMIN_ROLE is not assigned to a specific address, it becomes impossible to assign the URI_SETTER and MINTER_ROLE to new addresses. This could severely limit the functionality of the contract and could lead to a loss of control over the contract's operations if the initial addresses are compromised or the team wants to build new contracts that need to communicate with this NFT contract.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L41-L55

## Tool used
Manual Review

## Recommendation
To mitigate this issue, it is recommended to initialize the `DEFAULT_ADMIN_ROLE` to a specific account in the constructor. Alternatively, the `_setRoleAdmin` function could be used to allow a specific role to assign new addresses for each role. This would ensure that the `URI_SETTER` and `MINTER_ROLE` can be assigned to new addresses as needed, maintaining the functionality and security of the contract.

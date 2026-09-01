# [H] Any User can request loans for without depositing collateral

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/212
Type: sherlock-finding

## Details
cryptphi

high

# Any User can request loans for without depositing collateral

## Summary
The VaultImplementation.commitToLien() function allows any user to take loans on collateral token, this allows users to take loans on collateral tokens by calling the contract directly instead of through the AstariaRouter contract.

## Vulnerability Detail
In the call to commitToLien in a private Vault, any user is able to request for a loan on collateral token, this allows users to take loans on collateral tokens. However a user can mint collateral tokens without depositing any asset in the CollateralToken contract. The user can simply have a contract call the CollateralToken.onERC721Received() without any transfer to the collateraltoken contract, be issued a collateralToken and then call the private vault's commitToLien() to take a loan instead of making the call through AstariaRouter.

## Impact
Loss of funds

## Code Snippet
https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/CollateralToken.sol#L266-L296
https://github.com/sherlock-audit/2022-10-astaria/blob/main/src/VaultImplementation.sol#L242-L258

## Tool used
Manual Review

## Recommendation
If necessary, apply access control access on VaultImplementation.commitToLien() to be called by the Router only.

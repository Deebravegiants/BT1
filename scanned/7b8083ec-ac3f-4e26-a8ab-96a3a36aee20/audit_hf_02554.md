# [H] MJR-2 Incorrect logic when burning and minting tokens

## Summary
Severity: High
Contest weight: 0.0569
Dataset id: 13574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The mint() function defined at the line ERC20Facet.sol#L44 is for minting new tokens.
The amount of tokens is increased on the wallet with the address _receiver.
But the ERC-20 specification also uses the value of the totalSupply variable.
This variable is not incremented here.
At line: ERC20Facet.sol#L48. The burn() function is for burning tokens. The amount of tokens is reduced on the wallet with the address _from.
But the ERC-20 specification also uses the value of the totalSupply variable.
The value of this variable is not decremented here.
At the same time, the value of the variable totalSupply is used 7 times for calculations in this smart contract: BasketFacet.sol.

## Recommendation
This problem needs to be corrected so that the calculations would be correct.

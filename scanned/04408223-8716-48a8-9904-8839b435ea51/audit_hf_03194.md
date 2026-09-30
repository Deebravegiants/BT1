# [M] _validateDeploymentConfig function in NFT-

## Summary
Severity: Medium
Contest weight: 0.4054
Dataset id: 17769
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to not thoroughly checking all conditions of the deployment config, users might not be able to mint certain amount of tokens. In NFTCollection.sol, there is a function called _validateDeploymentConfig, which checks whether the deploymentConfig input to initialize function is valid. The function checks whether the maxSupply and tokensPerMint are greater than zero. But it never checks if the tokensPerMint is less than or equal to maxSupply. Suppose maxSupply < tokensPerMint. Then if the user calls a function which in-turn calls the _mintTokens function with an amount equal to tokensPerMint, it will revert. Even though he is technically trying to mint as per the rules. This is because the availableSupply() won't be greater than amount. 1. Dissatisfaction and Frustration of the user along with loss of his gas fees. 2. The contract would need redeployment as deployment config cannot be changed once its set.

## Recommendation
Add a require statement in the _validateDeploymentConfig function:
```solidity
require(config.tokensPerMint <= config.maxSupply, "Tokens per mint must be lte Maximum supply");
```

# [M] Reputation Risks with `contractOwner`

## Summary
Severity: Medium
Contest weight: 0.1528
Dataset id: 2379
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[DiamondCutFacet.sol](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/DiamondCutFacet.sol)  
[WithdrawFacet.sol](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/WithdrawFacet.sol)  
[DexManagerFacet.sol](https://github.com/code-423n4/2022-03-lifinance/blob/main/src/Facets/DexManagerFacet.sol)

`contractOwner` has complete freedom to change any functionality and withdraw/rug all assets. Even if well intended the project could still be called out resulting in a damaged reputation [like in this example](https://twitter.com/RugDocIO/status/1411732108029181960).

## Recommendation
Recommend implementing extra safeguards such as:

* Limiting the time period where sensitive functions can be used.
* Having a waiting period before pushed update is executed.
* Using a multisig to mitigate single point of failure in case `contractOwner` private key leaks.

> The bridges/swaps ecosystem is continually changing. Our mission is to allow seamless UX and provide users with new bridging and swapping routes **as fast as possible**. This comes at the cost of having some degree of centralization. We choose the Diamond standard to be able to constantly add new bridges and update the existing ones as they progress as well.
> 
> We agree with the increased safety of a DAO/Multisign mechanism and will provide them in the future. Timelocks are currently not planned, as we want to be able to react fast if we have to disable bridges for security reasons (e.g. if the underlying bridge is being exploited)

> Valid submission as user will approve fund to the contract.

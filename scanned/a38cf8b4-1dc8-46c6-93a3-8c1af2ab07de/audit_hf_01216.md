# [M] `massUpdatePools`

## Summary
Severity: Medium
Contest weight: 0.1644
Dataset id: 5417
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[ConvexMasterChef.sol#L178-L183](https://github.com/code-423n4/2022-05-aura/blob/main/convex-platform/contracts/contracts/ConvexMasterChef.sol#L178-L183)  

massUpdatePools() is a public function and it calls the updatePool() function for the length of poolInfo. Hence, it is an unbounded loop, depending on the length of poolInfo.  
If poolInfo.length is big enough, block gas limit may be hit.

## Proof of Concept
<https://consensys.github.io/smart-contract-best-practices/attacks/denial-of-service/#dos-with-block-gas-limit>

## Recommendation
I suggest to limit the max number of loop iterations to prevent hitting block gas limit.

Duplicate of [#147](https://github.com/code-423n4/2022-05-aura-findings/issues/147)

This is not a duplicate of Duplicate of [#147](https://github.com/code-423n4/2022-05-aura-findings/issues/147) and is also clearly documented as a potential issue in the code itself. If the admin were to accidentally add too many pools the contract would be affected, but the likelihood of this is low and if it were to happen, the admin could still turn off the pools and migrate to another contract. This would, however, affect the protocol in a severely negative way. Not fully updating all of the pools would potentially cause accounting issue and lead to loss of earned rewards. Given the impact and likelihood together, I think medium is actually reasonable in this case.

@LSDan- The `massUpdatePool()` function was found to be non-critical in previous contests (<https://github.com/code-423n4/2022-02-concur-findings/issues/161>) and when I filed the issue with Convex for their bug bounty, they rejected it saying it was a “non-issue” and didn’t meet their criteria for a bounty. Furthermore, ConvexMasterChef.sol is not listed as in scope for this contest: <https://github.com/code-423n4/2022-05-aura#contracts-of-interest>

@IllIllI000- Actually the scope was all non-test contracts, <https://github.com/code-423n4/2022-05-aura#repo>

@IllIllI000- Unlike the other contest, `massUpdatePools()` is used in this contract. I’m going to keep this as medium.

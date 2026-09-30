# [M] M-04 | Insufficient Gas

## Summary
Severity: Medium
Contest weight: 0.1492
Dataset id: 1988
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside releaseOnEid getSendOptions is used to calculate the amount of gas needed for the _lzReceive call. However due to rigid nature of the math and vast possible routes that the call could go, it would often result in an revert. Not only that but the math currently lacks the GAS_RESERVE, which is taken before that call is executed, resulting in the total gas allocated to be 30k + (20k * NFT count) Lets look into an example call: Total gas for 5 NFTs gets to be - 80k - 50k + 20k * 5 -> 130k
1. The call goes as usual executeMessage -> _executeMessage, but then we enter the else for _updateLockState
2. _updateLockState would in tern perform a couple of checks and call _clearDelegationsAndReleaseTokens if we are on the native chain
3. _clearDelegationsAndReleaseTokens would execute transferFrom for every NFT
4. This is followed by _clearDelegations which would call DELEGATE_REGISTRY.delegateERC721 again for every NFT Both transferFrom and delegateERC721 access storage, be it warm or cold, costing huge amounts of gas.

## Recommendation
Calculate the gas properly and make sure it covers all routes, even the most expensive one

# [M] M-08 | releaseOnEid In NFTShadow May Lead To DOS

## Summary
Severity: Medium
Contest weight: 0.1339
Dataset id: 1992
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The releaseOnEid function in NFTShadow assumes that we are only releasing to non native chains. This can be observed by the send calculations below function getSendOptions(uint256[] calldata tokenIds) public pure returns (bytes memory) {uint128 totalGasRequired = _BASE_OWNERSHIP_UPDATE_COST + (_INCREMENTAL_OWNERSHIP_UPDATE_COST * uint128(tokenIds.length)); returnOptionsBuilder.newOptions().addExecutorLzReceiveOption(totalGasRequired, 0);} The function assumes that we are always doing an ownership update but does not account for the fact that if we release to chain that includes the native collection that we will instead use delegations which are more expensive. This may result in a DOS due to not enough gas being sent to the destination chain to execute the message. However the tx can be retried after failure.

## Recommendation
If the Eid that we are releasing on includes that native collection, calculate the send costs to include all the delegations cost. After talks with dev this was the potential solution: maybe worth removing quotes and options generation from the Shadow and just using the Beacon

# [H] H-5 Incorrect function signature in

## Summary
Severity: High
Contest weight: 0.1395
Dataset id: 10279
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An incorrect function signature executeAdvancedGrant(MetaVesT.MetaVesTDetails) is used for abi.encodeWithSignature() in daoVoteGrantImplant.proposeAdvancedGrant() and daoVetoGrantImplant.proposeAdvancedGrant(). The selector in the proposalBytecode will be calculated incorrectly, and the future call to executeAdvancedGrant() will be impossible. daoVoteGrantImplant.sol#L234, daoVetoGrantImplant.sol#L344

## Recommendation
We recommend ﬁxing the signature to executeAdvancedGrant((address,bool,uint8,(uint256,uint256,uint256,uint256,uint256,uint256,uint128,uint128,uint160,uint48,uint48,uint160,uint48,uint48,address),(uint256,uint208,uint48),(uint256,uint208,uint48),(bool,bool,bool),(uint256,bool,address[])[]))

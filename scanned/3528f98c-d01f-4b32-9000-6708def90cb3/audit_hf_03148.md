# [H] OptimisticOracle.unbond can be tricked by malicious users

## Summary
Severity: High
Contest weight: 0.8812
Dataset id: 17669
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can bypass the check of OptimisticOracle.unbond.
OptimisticOracle.unbond checks whether the current proposal has not been made by msg.sender.
```solidity
if (
    proposals[rateId] == proposalId &&
    rateConfig.validator != address(0) &&
    IValidator(rateConfig.validator).canDispute(nonce)
) {
    revert OptimisticOracle__unbond_isProposing();
}
```
However, nonce and value is given by msg.sender. So proposalId is determined by msg.sender.
```solidity
function unbond(
    bytes32 rateId,
    uint256 value,
    bytes32 nonce,
    address receiver
) public {
    bytes32 proposalId = computeProposalId(
        rateId,
        msg.sender,
        value,
        uint256(nonce)
    );
    // Current proposal has not been made by `msg.sender` or it has passed `disputeWindow`
    // or the rateConfig has been unset
    RateConfig memory rateConfig = rateConfigs[rateId];
    if (
        proposals[rateId] == proposalId &&
        rateConfig.validator != address(0) &&
        IValidator(rateConfig.validator).canDispute(nonce)
    ) {
        revert OptimisticOracle__unbond_isProposing();
    }
    ...
}
```
Thus, the check of proposalId can be easily bypassed.
Proposers can easily bypass the check in OptimisticOracle.unbond and successfully take back their bond tokens when they are in the dispute window.

## Recommendation
Add a mapping for proposer and rateId: proposer[rateId] (Should be set in OptimisticOracle.shift).
Check proposer[rateId] instead of proposals[rateId].
```solidity
function unbond(
    bytes32 rateId,
    uint256 value,
    bytes32 nonce,
    address receiver
) public {
    bytes32 proposalId = computeProposalId(
        rateId,
        msg.sender,
        value,
        uint256(nonce)
    );
    // Current proposal has not been made by `msg.sender` or it has passed `disputeWindow`
    // or the rateConfig has been unset
    RateConfig memory rateConfig = rateConfigs[rateId];
    if (
        proposer[rateId] == msg.sender &&
        rateConfig.validator != address(0) &&
        IValidator(rateConfig.validator).canDispute(nonce)
    ) {
        revert OptimisticOracle__unbond_isProposing();
    }
    ...
}
```

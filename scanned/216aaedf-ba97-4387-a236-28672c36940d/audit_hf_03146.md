# [H] nonce could be malicious in OptimisticOracle.s

## Summary
Severity: High
Contest weight: 0.7641
Dataset id: 17659
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Proposers can use malicious nonce in OptimisticOracle.shift, since there is no check for nonce.
nonce is provided by the proposer. Thus, roundId and roundTimestamp can be malicious.
1. A malicious roundTimestamp can skip disputeWindow due to this issue https://github.com/SherlockAudit/fiat-dao/issues/31
2. A malicious roundId can cheat ChainlinkValidator.validate, e.g. Use old roundId, then ChainlinkValidator.validate can accept old value (which could be a bad value in the current round).
Proposers can use malicious nonce to set bad values. Bad values will be pushed to FIAT. It could lead to a big disaster in FIAT protocol.

## Recommendation
Add a check for nonce. Or let OptimisticOracle provide roundTimestamp and roundId instead of proposers.
Added a check in ChainlinkValidator.validate() that ensures the timestamp specified in the nonce is the same as the chainlink data round updatedAt timestamp. The checks in OptimisticOracle.shift() will ensure the nonce timestamp is passing our window checks and the validate() function should catch cases where a roundId was used with a different timestamp. I think this covers cases where old//malicious roundIds or timestamps are set via shift(). PR: https://github.com/fiatdao/delphi-v2/pull/5
```solidity
// Check that the feed timestamp matches the nonce
if (roundTimestamp != decodeRoundTimestamp(nonce)) {
    revert ChainlinkValidator__validate_invalidNonce();
}
```
revert means that dispute fail. Thus if roundId is invalid, no one can dispute the proposal.
Maybe, there can be a lastRoundId or latestRoundId to prevent that users use old roundId
You are correct, we should not revert in case of an invalid nonce, the dispute should be successful in that case. Also we should not revert on the disputeWindow if the nonce <-> roundTimestamp relation was not validated. I will update the flow to first validate the feed timestamp and only after that can it revert on dispute window passed. Also if the feed timestamp is not validated the dispute will always return success even if the proposed value somehow is correct (same as the computed one). This was a good catch, we changed the dispute to revert and obviously, I didn't consider all the implications.
So the global flow would be that the OptimisticOracle will validate that the nonce used for the dispute is the same as the nonce used in the proposal and if the validated nonce contains invalid chainlink data for eg invalid round timestamp then the dispute will be successful.
Updated the PR.
There is one minor issue still remains: when the original nonce is invalid, the dispute() should not continue using the wrong nonce in _settleDispute().
Maybe consider allowing the caller to specify another, correct nonce in this case?
https://github.com/fiatdao/delphi-v2/blob/96570ef83f978616ef4a4a6057f69364a1206c57/src/OptimisticOracle.sol#L289-L321
```solidity
function dispute(
    bytes32 rateId,
    address proposer,
    address receiver,
    uint256 value,
    bytes32 nonce
) external {
    RateConfig memory rateConfig = rateConfigs[rateId];
    if (rateConfig.validator == address(0))
        revert OptimisticOracle__dispute_rateConfigNotSet();
    // Validate the proposed value by fetching it from the corresponding Chainlink feed
    (bool proposalIsValid, uint256 verifiedValue) = IChainlinkValidator(
        address(rateConfig.validator)
    ).validate(
        value,
        address(uint160(uint256(rateId))), // RateId encodes the address of the token
        nonce // Nonce encoded the roundId and the roundTimestamp
    );
    // Proposal has to be invalid
    if (proposalIsValid) revert OptimisticOracle__dispute_invalidDispute();
    _settleDispute(
        rateId,
        proposer,
        receiver,
        value,
        verifiedValue,
        nonce,
        address(rateConfig.validator)
    );
}
```
https://github.com/fiatdao/delphi-v2/blob/96570ef83f978616ef4a4a6057f69364a1206c57/src/OptimisticOracle.sol#L331-L358
```solidity
function _settleDispute(
    bytes32 rateId,
    address proposer,
    address receiver,
    uint256 value,
    uint256 computedValue,
    bytes32 nonce,
    address validator
) private {
    if (proposer == validator) {
        revert OptimisticOracle__settleDispute_alreadyDisputed();
    }
    // Verify the proposal data
    if (
        proposals[rateId] !=
        computeProposalId(rateId, proposer, value, uint256(nonce))
    ) {
        revert OptimisticOracle__settleDispute_unknownProposal();
    }
    // Overwrite the proposal with the value computed by the Validator
    proposals[rateId] = computeProposalId(
        rateId,
        address(validator),
        computedValue,
        uint256(nonce)
    );
}
```
Updated the PR. Now the nonce will be computed by the validator. Mainly it will pack the propose timestamp with the provided validator data and the resulting nonce will be used to check the dispute / propose windows. This means that we can check the dispute window when we are attempting to make a new shift and the freshness of the provided data is now checked only in disputes (besides the regular checks). The validator created nonce contains the roundId, roundTimestamp, and the proposeTimestamp packed together.
We still need to update the test contracts to better reflect the changes and also add because of the issuer regarding malicious nonce double shifting we had to revisit how we create and use the nonce in the validation process. The PR for this issue has been closed and we are working on a separate PR that changes the nonce management and reorganizes the contract architecture a bit. We discussed this issue on discord have a separate review for delphi.
to Oct 5th.

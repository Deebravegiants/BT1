# [M] BlockSpecimenProofChain::submitBlockSpecimenProof can be abused to reduce session time

## Summary
Severity: Medium
Contest weight: 0.1910
Dataset id: 22429
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Block specimen producers submit specimens for a given block number during a limited time called a session. Any block producer can start a session by calling submitBlockSpecimenProof for a given block number. This means that a block specimen producer can start a session for a block which does not exist yet, and severely reduce the actual session time, since honest block specimen producer can only participate between the time the block has been created and the end of session. We can see that a session is started when the first specimen for the block height is submitted. This means that if a malicious block specimen producer has sent some invalid data for a block height which is in the future, the session is still started for that block. The following check ensures that a producer can not call submit for a block too far ahead:
require(block.number + allowedThreshold >= blockHeight, "Block too far ahead");
But since the default value for cd.allowedThreshold would be 100 blocks, and a session duration would be approximately 240 blocks, we can see that a malicious block producer can reduce the actual session duration for honest producers by half. The block specimen production session can be greatly reduced by a malicious producer (up to a half with current deploy parameters).

## Recommendation
Please consider starting the session at the estimated timestamp of the considered blockHeight:
- session.sessionDeadline = uint64(block.number + _blockSpecimenSessionDuration);
+ uint64 timestampOnDestChain = (blockHeight-cd.blockOnTargetChain)*cd.secondsPerBlock-cd.blockOnCurrentChain*_secondsPerBlock;
+ session.sessionDeadline = uint64(timestampOnDestChain + _blockSpecimenSessionDuration);

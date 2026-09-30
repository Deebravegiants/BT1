# [H] H-02 | DoS Of Deployment

## Summary
Severity: High
Contest weight: 0.2269
Dataset id: 2207
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Deploying with vm.startBroadcast() will lead to each call happening as a separate transaction. This gives a user who was distributed bTokens the opportunity to interact with the Uniswap pool prior to the first rebalance occurring. A malicious user can deploy liquidity below the desired BLV. Then, they can swap to their new deployed liquidity range. This will mean the active tick is below the BLV tick. When rebalance() is invoked, it will attempt to set the lower tick of the anchor range to the BLV tick and the upper tick will be calculated using the current active tick. Since the current active tick is below the BLV tick, setTicks() will revert due to InvalidTickRange. This will DoS the deployment after the tokens are distributed and the contract has been deployed.

## Proof of Concept
https://github.com/GuardianOrg/baseline-v2-team1/blob/POC_DOS_DEPLOYMENT/test/guardian/pocs/DoSDeployment.sol

## Recommendation
Deploy inside a smart contract function, so that the deployment happens atomically.

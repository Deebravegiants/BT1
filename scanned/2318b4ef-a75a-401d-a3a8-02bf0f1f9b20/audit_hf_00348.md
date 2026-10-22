# [M] claimIncentiveFor Might Lead To

## Summary
Severity: Medium
Contest weight: 0.1944
Dataset id: 1715
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol has introduces a functionality to claim an incentive for other claimants , this would require data for the claim and according to the sponsor (asked in thread) -> Signatures are available publicly by way of API , so this way I can claim for someone else , it's a neat feature but for CGDA incentive can be disastrous.
1.) Alice completes an action and for this action the incentive was a CGDAIncentive , the off chain mechanism verifies that Alice has performed the action successfully and grants her the claim , the claim as mentioned Signatures are available publicly by way of API
2.) Alice has a valid claim now for the CGDAIncentive , but she wants to wait for some time to claim since CGDA is dependent on lastClaimTime and she wants to maximise her gains , she wants to wait for 5 more blocks. ol/packages/evm/contracts/incentives/CGDAIncentive.sol#L124
3.) Bob comes and claims the incentive for Alice earlier -> ol/packages/evm/contracts/BoostCore.sol#L164 He does it such that Alice would get lesser incentive due to uint256 timeSinceLastClaim = block.timestamp - cgdaParams.lastClaimTime; being smaller than Alice intended and hence the rewards sent would be lesser ol/packages/evm/contracts/incentives/CGDAIncentive.sol#L123-L130
4.) Alice lost her incentives , she wanted to claim after 5 blocks and make maximum gains , but Bob ruined her returns. Alice will get way lesser incentives than intended due to Bob claiming on her behalf.

## Recommendation
Don't let users claim for other for such time dependent incentives.

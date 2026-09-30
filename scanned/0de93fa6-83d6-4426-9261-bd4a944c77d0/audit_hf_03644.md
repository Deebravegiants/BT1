# [M] Curve LP Controller withdraw and claim func-tion selector

## Summary
Severity: Medium
Contest weight: 0.1173
Dataset id: 19715
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function signature used for WITHDRAWCLAIM in both CurveLPStakingController.sol and BalancerLPStakingController.sol are incorrect, leading to the function not succeeding. In both the CurveLPStakingController.sol and BalancerLPStakingController.sol contracts, the function selector 0x00ebf5dd is used for WITHDRAWCLAIM. This selector corresponds to a function signature of withdraw(uint256,address,bool). bytes4 constant WITHDRAWCLAIM = 0x00ebf5dd; However, the withdraw() function in the Curve contract does not have an address argument. Instead, the function signature reads withdraw(uint256,bool), which corresponds to a function selector of 0x38d07436. Users who have deposited assets Curve pools will not be able to claim their rewards when they withdraw their tokens.

## Recommendation
Change the function selector in both contracts to 0x38d07436.

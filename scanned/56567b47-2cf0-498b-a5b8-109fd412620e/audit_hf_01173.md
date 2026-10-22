# [M] `BaseRewardPool4626` is not IERC4626 compliant

## Summary
Severity: Medium
Contest weight: 0.0985
Dataset id: 5030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[BaseRewardPool4626.sol](https://github.com/aurafinance/convex-platform/blob/9cae5eb5a77e73bbc1378ef213740c1889e2e8a3/contracts/contracts/BaseRewardPool4626.sol)  

BaseRewardPool4626 is not IERC4626 compliant.  
This makes the BaseRewardPool4626 contract irrelevant as it is for now since projects won’t be able to integrate with BaseRewardPool4626 using the [eip-4626](https://eips.ethereum.org/EIPS/eip-4626) standard.

## Recommendation
You can choose to remove the BaseRewardPool4626 and save on some deployment gas or review the necessary`functions` and `emits` required on [eip-4626](https://eips.ethereum.org/EIPS/eip-4626) and add it to BaseRewardPool4626.

Valid report. Probably should be severity 1 though.. no funds are ever at risk under any scenario.

I agree with medium risk here.

**[0xMaharishi (Aura Finance) resolved](https://github.com/code-423n4/2022-05-aura-findings/issues/26#event-6679177454):**
[code-423n4/2022-05-aura#5](https://github.com/code-423n4/2022-05-aura/pull/5)

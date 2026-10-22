# [M] M-06 | FeeRate Changes Lead To Loss Of Yield

## Summary
Severity: Medium
Contest weight: 0.1163
Dataset id: 2194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The setFeeRate function allows changing performance fee rates during an active period, which can result in users being charged different rates than what they initially agreed to. When users deposit funds, they implicitly agree to the current fee structure. However, if the fee rate is modified mid-period via setFeeRate, users will be charged the new rate when performance fees are calculated in updateStrategyFundAssets, even though this wasn't the rate in effect when they deposited. For example:
1. User deposits when fee rate is 20%
2. Mid-period, owner calls setFeeRate to change rate to 30%
3. At period end, performance fees are calculated using 30% rate
4. User pays higher fees than they agreed to when depositing

## Recommendation
Only allow fee rate changes to take effect in future periods. Or restrict fee rate changes to only occur after the current period's performance fees have been calculated.

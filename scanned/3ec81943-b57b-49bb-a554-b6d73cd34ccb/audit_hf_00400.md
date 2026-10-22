# [M] Precision loss in VaultManager#g

## Summary
Severity: Medium
Contest weight: 0.2573
Dataset id: 1786
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
On deposits and withdrawals, a balancing fee may or may not be charged, depending on the current reserve ratio in tranches: 1. Tranche#deposit -> ERC4626#previewDeposit -> Tranche#_deposit -> getDepositFeesTotal -> balancingFee; Tranche#withdraw -> ERC4626#previewWithdraw -> Tranche#_withdraw -> getWithdrawalFeesRaw -> balancingFee 2. Tranche#balancingFee -> VaultManager#getBalancingFee VaultManager.sol#L415-L429 As we can see, instead of bps, getDynamicReserveRatio returns percents. Therefore, if the actual reserve ratio is 6299 bps, it would return 62. in getBalancingFee: if ((getDynamicReserveRatio(tranche, isDeposit, assets) * 100) > balancingDeltaThreshold) { ,→ 62*100 < 6250 => getBalancingFee returns 0 instead of 500, despite the actual reserve ratio being outside of the target range so instead of paying the balancingFee because actual ratio is above 6250 (value from initializer), users will not. Similarly, when the ratio is between 3751 and 3799 bps, getDynamicReserveRatio would return 37, and balancingFee return a fee of 500, even though the current reserve ratio is within the target range. Percentage precision instead of bps in getDynamicReserveRatio. Internal pre-conditions getDynamicReserveRatio is in 3750-3799 or 6750-6799 bps range External pre-conditions Deposit or withdrawal into a Tranche. Deposits and withdrawals pay [do not pay] the balancingFee they shouldn't [should].

## Proof of Concept
Case 1: juniorTranche has 62_999e6 USDC seniorTranche has 37_101e6 USDC Alice wants to withdraw 100e6 from seniorTranche ratio = 62999e6 * 100 / 100_000e6 = 62 62*100 = 6200 6200 < 6250 balancingFee is not charged (but it should be) Case 2: seniorTranche has 62_001e6 USDC juniorTranche has 38_099e6 USDC Alice wants to withdraw 100e6 from juniorTranche ratio = 37_999e6 * 100 / 100_000e6 = 37 37*100 = 3700 3700 < 3750 balancingFee is charged (but it should not be)

## Recommendation
getDynamicReserveRatio should return bps instead of percentage; its return value should not be multiplied by 100 in getBalancingFee anymore.

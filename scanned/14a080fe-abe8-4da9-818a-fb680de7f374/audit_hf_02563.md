# [M] Insufficient Input Validation

## Summary
Severity: Medium
Contest weight: 0.2462
Dataset id: 13734
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
1. The following state variables are not validated in any regard: fundingPhaseDuration, fundingExchangeRatio, fundingRewardRate, terminalMaxLockDuration and amountToConvert in the constructor at initializing phase. This can lead to disfunction of the Portal due to the fact that all of these variables are immutable so they can not be changed after deployment time. Example scenarios are:
• If the deployer accidentally sets amountToConvert to zero. When the Portal has accrued some yield balance any user will be able to buy the yield with PSM tokens literally for free.
• If the deployer accidentally sets fundingRewardRate to zero, zero bTokens will be minted to the user when depositing PSM to provide an initial upfront yield.
• If fundingExchangeRatio is zero, then constantProduct will also be zero because of the internal calculations and buyPortalEnergy() function will most probably revert depending on the user-supplied _minReceived parameter or in the worst case scenario the portalEnergy of the user will remain the same after selling some PSM tokens.
• If fundingRewardRate rate is set to a large value, a massive amount of bTokens will be minted to the user which can later be burned to receive PSM and the protocol can be entirely drained.
• fundingPhaseDuration is an important value that determines when the Portal can be activated. The input value in the constructor should validate that it is within certain boundaries, for example, between several hours and 1 week (or any period that the developers agree on). Otherwise, the funding phase might be super short, not allowing anyone to fund the pool (e.g. 10 seconds), or it might last an exorbitant amount of time (e.g. 5 years).

2. Missing zero value check for the input amount in stake(), buyPortalEnergy(), sellPortalEnergy(), mintPortalEnergyToken(), burnPortalEnergyToken() and convert() functions. All of these functions lack zero value validation on important parameters. Setting invalid parameters in the best case will result in the waste of gas for their execution with zero amount as an input parameter. In the worst case in convert() function, for example, it can result in a large loss of funds for the user.

3. Missing zero address validation checks in convert() function and in the constructor. Despite the fact that it is expected to revert due to other validation checks, it is still the best practice to add zero address checks for all address input parameters in these functions. Nevertheless, it is helpful to add zero address validation checks to be consistent and ensure high availability of the protocol with resistance to accidental misconfigurations.

## Recommendation
Implement the corresponding validation checks and revert with custom errors if they are not met.

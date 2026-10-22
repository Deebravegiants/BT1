# [M] Partial redemptions should not be allowed when there are no staked validators left

## Summary
Severity: Medium
Contest weight: 0.2473
Dataset id: 9147
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In InstitutionalPirexEthWithdrawLogic.sol, initiateRedemption() adds pxEthAmount to pendingWithdrawal and proceeds to process pending withdrawals in multiples of DEPOSIT_SIZE. If pxEthAmount is still non-zero afterwards, the function will initiate a partial redemption by minting IUpxEth with the batchId of a future validator: if (pxEthAmount > 0) { pirexEthValidatorContracts.iupxEth.mint( receiver, pirexEthValidatorVars.batchId, pxEthAmount, "" ); } However, allowing partial redemptions for validators that haven't been unstaked might be problematic in an exit scenario where everyone is trying to redeem their institutional pxETH (e.g. migration to a new set of contracts). This is because there might be a case where IUpxEth is minted to a user for a future batchId, but there is no more staked validators to exit. As such, the IUpxEth can never be redeemed for ETH. For example:
• Assume everyone is trying to exit InstitutionalPirexEth:
– There is 1 staked validator left (32 ETH) and 31 ETH in the buffer.
– Alice holds 31 ETH worth of IPxEth, Bob holds 32 ETH worth of IPxEth.
– pendingWithdrawal = 0
• To avoid incurring the instant redemption fee, Alice calls initiateRedemption() with:
– _assets as all her IPxEth
– _shouldTriggerValidatorExit = false, since her 31 ETH is insufficient to trigger a validator exit
• Bob front-runs her transaction and calls initiateRedemption() to withdraw all his institutional pxETH:
– This triggers the exit of the last validator, and his IUpxEth has the batchId of the last validator
• When Alice's transaction is processed:
– pendingWithdrawal + postFeeAmount = 31 ETH, so _requiredValidators = 0 and this check passes
– Her withdrawal is a partial redemption, so the upxEth minted to her has the batchId of the next validator
• However, since there are no more validators to exit, her upxETH can never be redeemed.

## Recommendation
In InstitutionalPirexEthWithdrawLogic.initiateRedemption(), consider reverting if there aren't any staked validators left: if (pxEthAmount > 0) { + if (stakingValidators.count() == 0) revert Errors.NoValidatorsLeft(); pirexEthValidatorContracts.iupxEth.mint( receiver, pirexEthValidatorVars.batchId, pxEthAmount, "" ); } This prevents users from initiating partial redemptions for future validators when there are no staked validators remaining.

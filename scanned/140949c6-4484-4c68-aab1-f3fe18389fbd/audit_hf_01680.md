# [M] maxBufferSize isnt re-calculated when maxBufferSizePct changes in setMaxBufferSizePct()

## Summary
Severity: Medium
Contest weight: 0.2389
Dataset id: 9146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When maxBufferSizePct is modified by calling setMaxBufferSizePct(), the function does not re-calculate maxBufferSize according to the new value of maxBufferSizePct. Therefore, if maxBufferSizePct is decreased, maxBufferSize will be temporarily higher than what it should be. This only becomes a problem when slashValidator() is called on a Staking validator immediately after setMaxBufferSizePct(). slashValidator() calls InstitutionalPirexEthDepositLogic.addPendingDeposit() directly without re-calculating maxBufferSize beforehand: InstitutionalPirexEthDepositLogic.addPendingDeposit( ); Since maxBufferSize is still inflated, addPendingDeposit() will then fill up the buffer according to the outdated value of maxBufferSize: uint256 _remainingBufferSpace = ( pirexEthValidatorVars.maxBufferSize > pirexEthValidatorVars.buffer ? pirexEthValidatorVars.maxBufferSize - pirexEthValidatorVars.buffer : 0 ); For example:
• Assume the following:
– buffer = 32 ETH
– maxBufferSize = 64 ETH
– maxBufferSizePct is 30%
• Governance calls setMaxBufferSizePct() to decrease maxBufferSizePct to 15%:
– If maxBufferSize was re-calculated, it would be 32 ETH.
• slashValidator() is called to slash a validator with ValidatorStatus.Staking status. In addPendingDeposit():
– _remainingBufferSpace = 32 ETH, therefore the ETH from the slashed validator is added to the buffer.
• However, if maxBufferSize was updated to 32 ETH, the ETH from the slashed validator would have been added to pendingDeposit and used to stake a new validator.
As seen from the example above, due to the outdated value of maxBufferSize, ETH was wrongly added to the buffer instead of being used to stake a new validator. This will cause the protocol to generate less yield.

## Recommendation
Consider updating maxBufferSize in executeSetMaxBufferSizePct(): function executeSetMaxBufferSizePct( DataTypes.PirexEthValidatorVars storage pirexEthValidatorVars, + DataTypes.PirexEthValidatorContracts storage pirexEthValidatorContracts, uint256 pct ) external { InstitutionalPirexEthValidationLogic.validateSetMaxBufferSizePct(pct); emit SetMaxBufferSizePct(pct); pirexEthValidatorVars.maxBufferSizePct = pct; + pirexEthValidatorVars.maxBufferSize = + pirexEthValidatorContracts.pxEth.totalSupply() * pct / Constants.DENOMINATOR; }

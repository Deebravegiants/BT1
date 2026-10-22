# [H] executeInitiateRedemption() incorrectly calls initiateRedemption() with postFeeAmount

## Summary
Severity: High
Contest weight: 0.2461
Dataset id: 9144
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In InstitutionalPirexEthWithdrawLogic.sol, executeInitiateRedemption() calls initiateRedemption() with postFeeAmount: initiateRedemption( initiateRedemptionParams.depositSize, postFeeAmount, initiateRedemptionParams.receiver, initiateRedemptionParams.shouldTriggerValidatorExit ); However, _pxEthAmount should be passed to initiateRedemption() instead of postFeeAmount. postFeeAmount is the amount of institutional pxETH sent by the caller after fees have been subtracted, which has a 1:1 value with apxETH (note that the comment below is wrong): institutionalPxEth.transferFrom(msg.sender, address(this), assets); // Get the pxETH amounts for the receiver and the protocol (fees) (postFeeAmount, feeAmount) = InstitutionalPirexEthGenericLogic .computeAssetAmounts(fees, feeType, assets); However, initiateRedemption() expects the amount of pxETH to be redeemed, which would be _pxEthAmount. This causes initiateRedemption() to mint less upxETH to users upon withdrawal, causing a loss of funds.

## Recommendation
Pass _pxEthAmount instead of postFeeAmount: initiateRedemption( initiateRedemptionParams.depositSize, postFeeAmount, + _pxEthAmount, initiateRedemptionParams.receiver, initiateRedemptionParams.shouldTriggerValidatorExit );

# [H] TOFTOptionsReceiverModule will have the

## Summary
Severity: High
Contest weight: 0.6137
Dataset id: 22523
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
exerciseOptionsReceiver() will execute successfully, but lose (freeze permanently) all the output TAP amount of the user if being run with zero TAP amount (_options.tapAmount), which is valid use case of TapiocaOptionBroker's exerciseOption(), corresponding to the full position exercise.
```
TOFTOptionsReceiverModule's exerciseOptionsReceiver() will execute successfully, but lose (freeze permanently) all the output TAP amount of the user if being run with zero TAP amount (_options.tapAmount), which is valid use case of TapiocaOptionBroker's exerciseOption(), corresponding to the full position exercise. Specifying zero tap amount is a usual workflow of TapiocaOptionBroker's exerciseOption(), meaning that the whole eligible option position should be exercised. It's arguably the most used way to interact with exerciseOption() since slicing the exercise doesn't provide any additional benefits, but increases the operational and gas costs.

exerciseOptionsReceiver() will not revert when run with _options.tapAmount = 0, it will exercise the full position, but send nothing to the user: the whole TAP amount received will be left with the contract, being permanently frozen there as there is no way to rescue it. The probability of having exerciseOptionsReceiver() run with _options.tapAmount = 0 can be estimated as medium. The impact of user losing the whole position TAP proceedings, being permanently frozen with the contract, has high severity. Likelihood: Medium + Impact: High = Severity: High.

## Recommendation
Consider either forbidding zero _options.tapAmount in exerciseOptionsReceiver() or adding nonReentrant modifier to it, tracking TAP token balance and sending out the realized balance difference from TapiocaOptionBroker's exerciseOption() operation to the user instead of relying on _options.tapAmount.

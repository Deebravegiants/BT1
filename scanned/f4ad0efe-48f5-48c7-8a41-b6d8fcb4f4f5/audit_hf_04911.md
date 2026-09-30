# [M] USDT is not supported

## Summary
Severity: Medium
Contest weight: 0.1191
Dataset id: 22829
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When approving USDT, the allowance value needs to be set to 0 first before it can be used correctly. However, the 4.9.5 version of OpenZeppelin does not internally call forceApprove.
Users can perform swap operations using RouterSwapExecutor, but the actual amount used in params_.swapData.amountInSwap and params_.swapData.swapPayload can differ. For USDT, this will result in the contract being unable to use the pool again.
Additionally, other parts of the protocol are also affected. For example, in ValantisHOTModule.swap, setting the router to a specific SovereignPool and passing parameters that cause the actual balance used to be less than amountIn will result in the allowance not being 0. This prevents the module from directly interacting with the SovereignPool again.
The contract may not work properly

## Recommendation
It is recommended to upgrade openzeppelin

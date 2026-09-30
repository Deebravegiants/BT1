# [M] TU-1 | Call Return Value Gas Manipulation

## Summary
Severity: Medium
Contest weight: 0.0847
Dataset id: 18176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the withdrawAndSendNativeToken function, .call is used to send ether to the receiver address. Although bytes memory data is commented out, it will still be loaded into memory. A malicious receiver may load unexpectedly large return data into memory and potentially cause the keeper to expend more gas than expected. The size of the returned data that the receiver is able to generate is however constricted by the gasLimit, but this form of manipulation may still pose a risk to the system.

## Recommendation
Utilize a low level call to avoid loading the returned data into memory: assembly { success := call(gasLimit, receiver, amount, 0, 0, 0, 0) }

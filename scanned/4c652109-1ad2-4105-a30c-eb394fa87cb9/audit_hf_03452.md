# [M] IOU-1 | Overwritten Callback Contract

## Summary
Severity: Medium
Contest weight: 0.1331
Dataset id: 18862
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The saved callback contract is set anytime an IncreaseOrder is processed, therefore the following unexpected scenario may arise: 1) A trader creates a limit increase order for their position without a callback contract. 2) The trader now sends a market increase order with callback contract A to save contract A. 3) The trader’s limit increase order then executes. 4) The saved Callback contract is now overwritten with address(0), and upon liquidation or ADL, no callback action occurs. This may cause unexpected results for the trader considering the callback may be performing a useful action such as closing out a hedge/position on another platform. Additionally, the trader might only want the callback to be executed for their increase, and not on any subsequent liquidation or ADL.

## Recommendation
Remove the setSavedCallbackContract function from the IncreaseOrder flow so it can be set explicitly with a separate configuration function. Additionally, clearly document that there can only be 1 saved callback contract per market e.g. if a user has two positions long and short in the same market both will use the same callback contract.

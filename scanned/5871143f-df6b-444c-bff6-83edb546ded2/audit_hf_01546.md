# [M] ConnextRouter fails to record failed message if gas sent is not enough

## Summary
Severity: Medium
Contest weight: 0.1099
Dataset id: 8226
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ConnextRouter places the xBundleConnext(...) call on a try/catch block to prevent failed actions to make the transaction revert and the funds being given to Connext. The EVM saves 1/64th of gas before an external call to try to finish execution after the external call. However, if the xBundleConnext(...) transaction inside the try/catch fails, the following execution consumes a non significant amount of gas (transferring and recording the failed message), such that 1/64 of the sent gas could not be enough to finish the execution.

## Recommendation
Calculate the minimum amount required of gas to finish execution after the try/catch block and revert if this gas is not available prior to the block with gasleft(). This ensures that whatever actions users do inside the try/catch block, the message will always be recorded if it fails.

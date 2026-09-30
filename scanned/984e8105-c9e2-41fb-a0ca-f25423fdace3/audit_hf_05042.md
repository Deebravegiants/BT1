# [M] Silent Failure in Must- NewDecFromString Can Lead to Node Crashes The protocol has acknowledged this issue.

## Summary
Severity: Medium
Reporter: defsec
Contest weight: 0.1293
Dataset id: 23046
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The use of MustNewDecFromString in the AlloraExecutor's ExecuteFunction method ignores potential errors, which can lead to invalid parameters being passed to the node, causing crashes.
In the ExecuteFunction method of the AlloraExecutor, MustNewDecFromString is used to convert string values to decimal types. This function panics if it encounters an error during conversion, rather than returning an error that can be handled gracefully. The code doesn't have any error handling or recovery mechanism for these potential panics.
For example:
can crash the node if not caught.
Similar issues exist for other conversions in the code, such as those for forecaster values and various attributed values.
• Malicious actors could potentially exploit this to crash nodes by providing invalid input data.
• Unexpected panics can cause the node to crash.

## Recommendation
Consider adding err check on the node software.
if err != nil {
return result, fmt.Errorf("invalid inferer value: %w", err)
}

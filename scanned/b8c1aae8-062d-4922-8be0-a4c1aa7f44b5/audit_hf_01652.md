# [H] TransferFrom is incorrectly treated as a view function

## Summary
Severity: High
Contest weight: 0.2369
Dataset id: 8862
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the execute function of the MultiCurrencyPrecompile module, the check_function_modifier is intended to ensure that function calls are compatible with the execution context, particularly regarding whether they are payable or non-payable functions. However, the Function::TransferFrom case is missing from the match statement:
handle.check_function_modifier(match selector {
    Function::Transfer => FunctionModifier::NonPayable,
    // Function::TransferFrom is not included here
    _ => FunctionModifier::View,
As a result, TransferFrom defaults to FunctionModifier::View, which is incorrect because TransferFrom is a state-changing function that should be marked as non-payable. Treating it as a view function can lead to unexpected errors or failures when it's invoked, as the execution environment might restrict state changes in contexts meant for view-only operations.

## Recommendation
Include Function::TransferFrom in the check_function_modifier match statement and assign it FunctionModifier::NonPayable, similar to the Transfer function:
handle.check_function_modifier(match selector {
    Function::Transfer => FunctionModifier::NonPayable,
    Function::TransferFrom => FunctionModifier::NonPayable, // Add this line
    _ => FunctionModifier::View,

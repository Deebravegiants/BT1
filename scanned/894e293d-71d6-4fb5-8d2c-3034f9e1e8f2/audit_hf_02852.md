# [M] Inconsistant stack in execute_fa_withdrawal

## Summary
Severity: Medium
Contest weight: 0.1565
Dataset id: 15945
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the new logic of execute_fa_withdrawal, on L207, a new execution stack is pushed by handler.begin_inter_transaction. It then enters inner_execute_withdrawal with Rust's ? syntax. Later lines we also calls inner_execute_proxy also with Rust's ? syntax.
If an error happens in either function, the function returns directly without any further clean up code, meaning that the handler.end_inter_transaction will not be called. In this case, the "transaction stack" will become inconsistent. At this stage, SputnikVM can guarantee nothing, not even correctly returning an ExitFatal error.
We rate this as medium severity, as we believe that there's a particularly high risks that some forms of the bug may be exploitable during a system upgrade. From the author's experience with other blockchains of similar stacks, it's particularly likely, even in production environment, that some small amount of storage values may become unparsable due to incorrect migrations. At that moment, read_u256_le_default in the TicketTable will trigger this bug.

## Recommendation
Do not use the ? syntax but handle all errors manually and always remove the entered call stack.
Alternatively, wrap the logic between enter/exit call stack into a separate function and only use ? syntax there.

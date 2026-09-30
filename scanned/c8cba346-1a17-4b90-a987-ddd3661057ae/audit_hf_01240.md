# [H] The same message can be marked as executing multiple times without being executed

## Summary
Severity: High
Contest weight: 0.1389
Dataset id: 5741
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the op-program retrieves executing messages by parsing logs from the block receipts. Each log in the block is passed to DecodeExecutingMessageLog. If an ExecutingMessage log coming from the CrossL2Inbox contract is found, it is collected in execMsgs for processing. However, the current implementation of CrossL2Inbox allows emitting multiple times the same ExecutingMessage log without actually executing the message.

## Recommendation
Executing multiple times the same processing should be avoided. op-program could check for duplicated executing messages. Another way to fix the issue is to limit the ExecutingMessage log in CrossL2Inbox to one per message.

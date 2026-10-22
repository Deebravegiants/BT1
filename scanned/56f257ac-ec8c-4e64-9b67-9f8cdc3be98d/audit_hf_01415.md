# [M] Disabled router enrollment check allows processing of unroutable messages

## Summary
Severity: Medium
Contest weight: 0.3817
Dataset id: 7304
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In hyperlane-monorepo/move/mailbox/sources/mailbox.move L136, the handle_message function has a commented out router enrollment check:
```solidity
// router::assert_router_should_be_enrolled<T>(src_domain, sender_addr);
```
This check would have verified that a router exists for the message's source domain. Without it, messages from domains without enrolled routers can be processed through inbox_process(), but will likely become stuck as they cannot be routed to their final destination. This wastes resources and could lead to permanently stranded messages.

## Recommendation
Uncomment and restore the router enrollment verification.

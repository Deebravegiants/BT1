# [?] Fix potential race condition in node-relay (#1716)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2021-03-08
Source: https://github.com/ACINQ/eclair/commit/ea8f94022e734aaca189ae1288fc00197907a19f
Type: security-commit

## Details
Fix potential race condition in node-relay (#1716)

We previously relied on `context.child` to check whether we already had a
relay handler for a given payment_hash.

Unfortunately this could return an actor that is currently stopping itself.
When that happens our relay command can end up in the dead letters and the
payment will not be relayed, nor be failed upstream.

We fix that by maintaining the list of current relay handlers in the
NodeRelayer and removing them from the list before stopping them.
This is similar to what's done in the MultiPartPaymentFSM.

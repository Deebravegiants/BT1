# [?] fix: estimateFee panic w/ missing required fields (#2770)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-04-18
Source: https://github.com/NethermindEth/juno/commit/8880dcd0e8d90cda359ab03e48fb4e0fb1e7b7f7
Type: security-commit

## Details
fix: estimateFee panic w/ missing required fields (#2770)

* fix: estimateFee panic w/ missing required fields

Closes #2475

This PR fixes the issue by doing the following:

1. Adding checks for the fields at `prepareTransactions`
2. Using a struct for `ResourceBounds` instead of the map, which
   enforces the required fields when `ResourceBounds` is provided.

The change of using a struct for the `ResourceBounds` does mean that
there is a need to manually copy over the values since copy does not
convert the rpc `ResourceBounds` to core `ResourceBound` automatically.

When fixing the issue, also found several concerning points:

1. Since `omitempty` takes precedence over the `validate` tag, is there
   some other fields currently/in the future that might cause the same issue?
2. Since this bug exists for all version of rpc, maintaining multiple
   rpc directory might not be a good idea, maybe there's a method to
better consolidate the different rpc versions?

* refactor: reuse rpc types & clean up comparisons

# [?] Fix panic when Executor is used with dev mode (#1562)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2024-03-18
Source: https://github.com/risc0/risc0/commit/8a42c07a24dae9715e42661cba31ddc9a02ccaae
Type: security-commit

## Details
Fix panic when Executor is used with dev mode (#1562)

I ran into an issue where, in using `risc0-zkvm` with the `client`
feature and `RISC0_DEV_MODE=1` I would get a panic. I tracked this down
to the way null segment refs were being handled, which is that deep
within the executor the provided callback was being ignored in dev mode.
I believe the root cause of the panic then was that dev mode was being
checked for at the wrong layer of abstraction.

In this PR, the decision on using `NullSegmentRef` is moved by have the
dev mode `ProverServer` implementation use `null_callback` in
`prove_with_context`. Additionally, the `LocalProver` impl of `Executor`
is altered to avoid calling `resolve` on the segments such that they
never need to be stored, and we are still able to construct the
`SessionInfo`.

This PR also cleans up some links that cause `cargo doc -Fclient` to
fail, and prunes `EmptySegmentRef`, which is redundant to
`NullSegmentRef` and not exported anywhere.

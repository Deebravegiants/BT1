# [?] fix(nns-recovery): panic on first failed NP action (#8185)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-12-23
Source: https://github.com/dfinity/ic/commit/abc7ecd5e22698cd6962be53e3f8dbdf3709b599
Type: security-commit

## Details
fix(nns-recovery): panic on first failed NP action (#8185)

On the NNS recovery system test where NP actions are simulated
sequentially, we were swallowing errors of such actions. This PR makes
the test panic on the first failed NP action, instead of continuing as
if nothing happened.

Example: this
[run](https://dash.zh1-idx1.dfinity.network/invocation/e244d28b-902a-47a1-9425-89b2f38c1b6d?target=%2F%2Frs%2Ftests%2Fnested%2Fnns_recovery%3Anr_seq_np_actions&targetStatus=6#@3247)
had two failed NP actions resulting in two panics in the tokio workers,
but still went forward and "Ensure the subnet is healthy after the
recovery".

PS: On the other system tests where the actions are simulated in
parallel, the `join_all` [correctly
panics](https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html#method.join_all)
on the first error.

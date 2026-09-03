# [?] fix(consensus): Avoid panicking when validation result channel is closed (#10099)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-11-17
Source: https://github.com/ZcashFoundation/zebra/commit/d3131af402cf2dd8629aa1f93b6aeae52c7347ec
Type: security-commit

## Details
fix(consensus): Avoid panicking when validation result channel is closed (#10099)

* Avoids finishing batch worker task when batch result channel has been closed when attempting to broadcast validation results.

Avoids panicking when batch worker task has finished by returning an error early without polling the completed JoinHandle.

* Corrects `tower_batch_control::Worker::failed()` method docs.

* Removes logic from `Batch::poll_ready` for returning an error early when the worker task is finished and replaces it with a correctness comment.

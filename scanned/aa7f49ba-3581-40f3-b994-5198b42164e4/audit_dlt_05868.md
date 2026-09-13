# [?] fix(prover-autoscaler): fix resource exhaustion detection and aggr mode (#4733)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-03-24
Source: https://github.com/matter-labs/zksync-era/commit/f3d81ced085270a086875ac6187dbee953635831
Type: security-commit

## Details
fix(prover-autoscaler): fix resource exhaustion detection and aggr mode (#4733)

## What ❔

- Replace dead "GCE out of resources" event detection with actual
`FailedScheduling/Insufficient nvidia.com/gpu` events from k8s
scheduler. The old string match was not observed.
- Exclude disabled pools (max_replicas=0) from aggressive mode threshold
calculation — they inflate the denominator and can never have errors,
making the threshold (almost) unreachable in practice.

## Why ❔

Stabilize autoscaling during worst case scenarios

## Is this a breaking change?
- [x] Yes
- [ ] No

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

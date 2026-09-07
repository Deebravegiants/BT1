# [?] fix: deflake //rs/tests/nested/nns_recovery:nr_broken_dfinity_node by allowing panic (#10041)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-04-28
Source: https://github.com/dfinity/ic/commit/c0e7ce860f5aecf3fafcc742dae0d91dc00aadd9
Type: security-commit

## Details
fix: deflake //rs/tests/nested/nns_recovery:nr_broken_dfinity_node by allowing panic (#10041)

The test performs a `systemctl restart ic-replica` which causes a
SIGTERM to be sent to the replica process which sometimes causes the
sandbox_execution_controller to panic with:
"Sandboxed_execution_controller reply channel closed unexpectedly" which
we now allow in all tests.

# [?] Fix flaky test_maximum_full_file_count by eliminating race condition (#20704)

## Summary
Severity: Unknown
Chain: Chia
Component: Chia-Network/chia-blockchain
Published: 2026-03-25
Source: https://github.com/Chia-Network/chia-blockchain/commit/309c279313bc61d8ee98c39da0d000aee23b432e
Type: security-commit

## Details
Fix flaky test_maximum_full_file_count by eliminating race condition (#20704)

* Fix flaky test_maximum_full_file_count by eliminating race condition

The test fails intermittently on macOS CI because farm_block_with_spend
polls the mempool with a blind timeout. When the wallet builds a spend
against stale singleton state, the full node rejects it
(INVALID_SPEND_BUNDLE, status 3), the mempool never reaches count 1,
and the test burns 30 seconds before failing with a misleading timeout.

Three fixes:

1. Add check_mempool_spend_count_or_fail() that inspects the
   transaction's sent_to field on each poll. If any entry has
   MempoolInclusionStatus.FAILED, raise immediately with the rejection
   reason instead of waiting for the timeout.

2. Add a singleton readiness check (check_singleton_confirmed) after
   farm_block_with_spend in the test loop, ensuring the DataLayer
   wallet has processed the previous block's singleton update before
   the next batch_update builds a new spend.

3. Change check_mempool_spend_count to use >= instead of == so
   auto-resends or ancillary transactions don't break the check.

Made-with: Cursor

* Add pragma: no cover to defensive error-handling paths

The check_mempool_spend_count_or_fail helper's RuntimeError raise and
ValueError catch are defensive paths that only fire on mempool rejection
or unexpected errors — neither occurs during happy-path test runs.
Marking them with pragma: no cover matches the existing convention used
throughout this file and resolves the Coveralls coverage gap.

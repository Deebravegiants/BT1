# [?] Fix - overflow in `test_serialize_parameters_with_many_accounts()` (#7599)

## Summary
Severity: Unknown
Chain: Solana
Component: jito-foundation/jito-solana
Published: 2025-08-22
Source: https://github.com/jito-foundation/jito-solana/commit/83d40ef2be8ed0a63bbf9346d3746006da4778c5
Type: security-commit

## Details
Fix - overflow in `test_serialize_parameters_with_many_accounts()` (#7599)

* Adds back the debug_assert!() in TransactionContext::configure_next_instruction_for_tests().

* Adjusts test_serialize_parameters_with_many_accounts() to avoid the overflow.

* Uses MAX_ACCOUNTS_PER_TRANSACTION for dedep_map len.

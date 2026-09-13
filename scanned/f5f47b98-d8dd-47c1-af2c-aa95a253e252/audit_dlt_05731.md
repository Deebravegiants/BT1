# [?] fix(state): Write database format version to disk atomically to avoid a rare panic (#8795)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2024-08-29
Source: https://github.com/ZcashFoundation/zebra/commit/0ef9987e9eeaae4d9af121264f66a866501d4cee
Type: security-commit

## Details
fix(state): Write database format version to disk atomically to avoid a rare panic (#8795)

* Splits `atomic_write_to_tmp_file` out of `zebra_network::Config::update_peer_cache`

* Uses the new `atomic_write_to_tmp_file` fn in `update_peer_cache()`

* Replaces repetitive code for getting the default peer and state cache directories with `default_cache_dir()`

* Converts `atomic_write_to_tmp_file` to a blocking function and adds `spawn_atomic_write_to_tmp_file` for use in async environments.

* Uses `atomic_write_to_tmp_file` to write database versions to disk

* Removes `spawn_atomic_write_to_tmp_file()` and inlines its body at its callsite to avoid adding tokio as a dependency of zebra-chain.

* Apply suggestions from code review

Co-authored-by: Marek <mail@marek.onl>

---------

Co-authored-by: Marek <mail@marek.onl>

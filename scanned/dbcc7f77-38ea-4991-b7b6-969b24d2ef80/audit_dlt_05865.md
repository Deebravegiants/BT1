# [?] chore(rust): remove stale RUSTSEC-2026-0002 ignore (#19598)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-17
Source: https://github.com/ethereum-optimism/optimism/commit/9cb57b0a8e3646c5a10eaa0c0c817c9765a54706
Type: security-commit

## Details
chore(rust): remove stale RUSTSEC-2026-0002 ignore (#19598)

* chore(rust): remove stale RUSTSEC-2026-0002 ignore from deny.toml

The lru crate advisory (RUSTSEC-2026-0002) no longer matches any crate
in the dependency tree, causing cargo-deny to fail with
"advisory was not encountered". The vulnerable lru versions (0.9.0–0.16.2)
have been patched — lru 0.16.3 is already in Cargo.lock.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* chore: Update lz4_flex to 0.12.1

lz4_flex 0.12.0 suffers from RUSTSEC-2026-0041

https://rustsec.org/advisories/RUSTSEC-2026-0041

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Co-authored-by: wwared <541936+wwared@users.noreply.github.com>

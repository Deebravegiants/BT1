# [?] chore: ignore lru unsoundness advisory, drop stale sized-chunks ignore (#12646)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-08-12
Source: https://github.com/iotaledger/iota/commit/7ad9cdea433cfe73231672abd660354653b01682
Type: security-commit

## Details
chore: ignore lru unsoundness advisory, drop stale sized-chunks ignore (#12646)

# Description of change

`cargo deny check advisories` fails on `develop` (it only runs nightly,
not on PRs), and also warns about an ignore that no longer matches
anything. This gets it back to `advisories ok`:

- Ignores `RUSTSEC-2026-0253` (`LruCache::pop()` is not panic-safe). The
fix is `lru` 0.18.2, blocked by the same msim determinism problem
already documented for `RUSTSEC-2026-0002` in `deny.toml` — bumping it
aborts `test_passive_reconfig_determinism` with `non-determinism
detected`, as that comment predicts (details in the comment below). None
of the key types stored in our caches have a `Drop` that can panic, so
the unsound path isn't reachable here.
- Drops the `RUSTSEC-2023-0126` ignore, which stopped matching once the
lockfile picked up a patched `sized-chunks`.

Dropping the ignore instead of getting off `lru` 0.12 would mean
changing the determinism machinery — the `LruCache` warm-up in
`iota_macros::sim_test`, or a fixed hasher for the caches reachable from
sim tests. Worth its own PR if an ignore isn't good enough for a
use-after-free.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)

`cargo deny check advisories` reports `advisories ok` with no
`advisory-not-detected` warnings. The yanked `spin` 0.9.8 warning is
pre-existing on `develop` and untouched.

Co-authored-by: Claude <noreply@anthropic.com>

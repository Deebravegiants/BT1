# [?] chore(ci): ignore quick-xml RUSTSEC-2026-0194/0195 in cargo-audit (#16015)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-07-02
Source: https://github.com/near/nearcore/commit/b4a43939699d38b1191f97b238a8dc0196256099
Type: security-commit

## Details
chore(ci): ignore quick-xml RUSTSEC-2026-0194/0195 in cargo-audit (#16015)

## Background

A newly-published advisory pair (2026-06-29) fails the `Cargo Audit` CI
check on master and every open PR:

- **RUSTSEC-2026-0194** / **RUSTSEC-2026-0195** — `quick-xml`
quadratic-runtime DoS, fixed in `>= 0.41.0`.

`quick-xml` (0.32.0 / 0.36.2 / 0.38.4) is only reachable transitively
via `rust-s3`, `aws-creds`, and `object_store`, none of which have a
release that uses `quick-xml 0.41` yet, so the advisory can't be cleared
by a dependency bump. It's used solely to parse trusted S3/cloud-storage
XML responses, not untrusted input.

## What changed

- Add `RUSTSEC-2026-0194` and `RUSTSEC-2026-0195` to the
`.cargo/audit.toml` ignore list, with a note to remove them once the
upstream S3 crates upgrade.
- Correct the stale `RUSTSEC-2026-0097` comment: RustSec lists `rand >=
0.8.6` as a patch (the comment claimed 0.8.x had none). The advisory
remains non-triggering here regardless.

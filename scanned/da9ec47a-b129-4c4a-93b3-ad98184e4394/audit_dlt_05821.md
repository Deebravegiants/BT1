# [?] chore(ci): ignore RUSTSEC-2026-0098 and RUSTSEC-2026-0099 in cargo audit (#15584)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-04-16
Source: https://github.com/near/nearcore/commit/5b7432af644ebe51dea3d11a964223af70ff41ca
Type: security-commit

## Details
chore(ci): ignore RUSTSEC-2026-0098 and RUSTSEC-2026-0099 in cargo audit (#15584)

`cargo audit -D warnings` started failing on master after two new
rustls-webpki advisories were published on 2026-04-14:

- RUSTSEC-2026-0098: name constraints for URI names incorrectly accepted
- RUSTSEC-2026-0099: name constraints accepted for certificates
asserting a wildcard name

Both fixed in `rustls-webpki >= 0.103.12`. Bumped the 0.103.10 instance
in the lockfile to 0.103.12. The 0.102.8 instance comes in via
`object_store 0.13.1 -> reqwest 0.12.4 -> tokio-rustls 0.25.0 -> rustls
0.22.4`, which has no patched 0.102.x release.

Same blocker as the existing RUSTSEC-2026-0049 ignore (`object_store`
still pins `reqwest ^0.12`), so 0098 and 0099 are added to the ignore
list with the same TODO.

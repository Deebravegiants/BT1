# [H] libcrux has All-Zero Key Generation Upon Catastrophic RNG Failure

## Summary
Severity: High
Advisory: GHSA-434v-x5qv-pmh6
CWE: CWE-1240, CWE-331, CWE-392
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-434v-x5qv-pmh6
Type: github-advisory

## Affected
- crates.io: `libcrux-ed25519` — affected >=0 <0.0.7

## Details
The libcrux-ed25519 key generation samples Ed25519 secret keys from a provided CSPRNG in a loop for up to 100 attempts until a non-zero key is found.  If a non-zero key could not be sampled within 100 attempts the key generation function would silently continue with an all-zero buffer as the secret key.

## Impact
This bug only occurs in the event of a catastrophic failure of the CSPRNG, but would allow anyone to forge signatures under the resulting static signing key.

## Mitigation
Instead of silently continuing with an all-zero signing key, starting from version `0.0.7` key generation will error in the case of 100 failed attempts at sampling a valid key.

## References
- https://github.com/cryspen/libcrux/pull/1349
- https://github.com/cryspen/libcrux
- https://rustsec.org/advisories/RUSTSEC-2026-0075.html

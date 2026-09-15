# [H] Nimiq network-libp2p: DHT query poisoning via first-record verification failure

## Summary
Severity: High
Advisory: CVE-2026-46541
Aliases: GHSA-ccqv-2c9q-mqw5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46541
Type: osv

## Details
Nimiq is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.4.0, iIn handle_dht_get(), the DhtResults accumulator is only initialized when the first DHT record passes verification. If the first record fails (from a malicious DHT node), DhtResults is never created, and all subsequent valid records are discarded with "DHT inconsistent state" errors. This issue has been patched in version 1.4.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46541.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-ccqv-2c9q-mqw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46541
- https://github.com/nimiq/core-rs-albatross/pull/3707

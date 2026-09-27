# [M] Nimiq network-libp2p: Untrusted peer can wedge DHT

## Summary
Severity: Medium
Advisory: CVE-2026-44505
Aliases: GHSA-g39c-jcgg-qwvr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-44505
Type: osv

## Details
Nimiq is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. network-libp2p handles kad get-record query progress in handle_dht_get (network-libp2p/src/swarm.rs). Prior to version 1.4.0, when a peer returns a FoundRecord, the code verifies the record via dht_verifier.verify(&record.record). On verifier error, handle_dht_get logs and returns early without completing the oneshot used by Network::dht_get, and without cleaning up per-query bookkeeping. Later query progress can hit the "DHT inconsistent state" path and also return without cleanup. Because Network::dht_get awaits the oneshot without a timeout, the caller future can hang indefinitely. This issue has been patched in version 1.4.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44505.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-g39c-jcgg-qwvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44505
- https://github.com/nimiq/core-rs-albatross/pull/3716

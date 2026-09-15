# [M] Kraken Agents Peer-to-Peer Download Cache Poisoning via Digest Verification Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-75625
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75625
Type: osv

## Details
Kraken agents fail to verify peer-to-peer downloaded blobs against their requested SHA-256 digest before committing to the content-addressable cache, relying only on CRC32 checksums for piece validation. Attackers on the agent-to-agent path or malicious peers can supply substituted content with forged CRC32 corrections that passes per-piece checks, poisoning the cache with attacker-chosen container image layers or manifests that are re-seeded and executed by other hosts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75625.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75625
- https://www.vulncheck.com/advisories/kraken-agents-peer-to-peer-download-cache-poisoning-via-digest-verification-bypass
- https://github.com/uber/kraken/issues/638
- https://github.com/uber/kraken
- https://github.com/uber/kraken/blob/master/lib/torrent/storage/agentstorage/torrent.go

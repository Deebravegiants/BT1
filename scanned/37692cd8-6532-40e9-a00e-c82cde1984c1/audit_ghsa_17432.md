# [H] Elasticsearch Packetbeat has Excessive Allocation of Memory and CPU via Malicious IPv4 Fragments

## Summary
Severity: High
Advisory: GHSA-fj69-23m4-ccvv
CVE: CVE-2025-68388
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-fj69-23m4-ccvv
Type: github-advisory

## Affected
- Go: `github.com/elastic/beats` — affected >=8.6.0 <8.19.9
- Go: `github.com/elastic/beats` — affected >=9.0.0 <9.1.9
- Go: `github.com/elastic/beats` — affected >=9.2.0 <9.2.3
- Go: `github.com/elastic/beats/v7` — affected >=0 <7.0.0-alpha2.0.20251209162832-28cfc80d2f4e

## Details
Allocation of resources without limits or throttling (CWE-770) allows an unauthenticated remote attacker to cause excessive allocation (CAPEC-130) of memory and CPU via the integration of malicious IPv4 fragments, leading to denial-of-service in Packetbeat.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68388
- https://github.com/elastic/beats/commit/28cfc80d2f4e80bfd1c72eb3f849d777751ab870
- https://discuss.elastic.co/t/packetbeat-8-19-9-9-1-9-and-9-2-3-security-update-esa-2025-29/384177
- https://github.com/elastic/beats

# [H] Kamailio Core: TCP Data Processing Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-39863
Aliases: GHSA-2wj4-f825-2h2f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-39863
Type: osv

## Details
Kamailio is an open source implementation of a SIP Signaling Server. Prior to 6.1.1, 6.0.6, and 5.8.8, an out-of-bounds access in the core of Kamailio (formerly OpenSER and SER) allows remote attackers to cause a denial of service (process crash) via a specially crafted data packet sent over TCP. The issue impacts Kamailio instances having TCP or TLS listeners. This vulnerability is fixed in 5.1.1, 6.0.6, and 5.8.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39863.json
- https://github.com/kamailio/kamailio/security/advisories/GHSA-2wj4-f825-2h2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-39863

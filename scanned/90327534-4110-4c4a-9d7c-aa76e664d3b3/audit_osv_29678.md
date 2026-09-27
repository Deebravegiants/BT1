# [H] Quicly assertion failures

## Summary
Severity: High
Advisory: CVE-2024-45396
Aliases: GHSA-mp3c-h5gg-mm6p
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-11
Source: https://osv.dev/vulnerability/CVE-2024-45396
Type: osv

## Details
Quicly is an IETF QUIC protocol implementation. Quicly up to commtit d720707 is susceptible to a denial-of-service attack. A remote attacker can exploit these bugs to trigger an assertion failure that crashes process using quicly. The vulnerability is addressed with commit 2a95896104901589c495bc41460262e64ffcad5c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45396.json
- https://github.com/h2o/quicly/security/advisories/GHSA-mp3c-h5gg-mm6p
- https://nvd.nist.gov/vuln/detail/CVE-2024-45396
- https://github.com/h2o/quicly/commit/2a95896104901589c495bc41460262e64ffcad5c

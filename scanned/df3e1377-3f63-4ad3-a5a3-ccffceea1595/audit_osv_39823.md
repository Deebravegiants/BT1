# [M] Misskey: JSON-LD signature validation + compaction is vulnerable to timing attacks

## Summary
Severity: Medium
Advisory: CVE-2026-47746
Aliases: GHSA-38jx-423m-g387
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-47746
Type: osv

## Details
Misskey is an open source, federated social media platform. Versions 12.37.0 and later, but prior to 2026.5.4, are vulnerable to timing attacks during JSON-LD signature validation and the compaction process. Because the JSON-LD parsing context is not shared between signature verification and subsequent processing, the application may trust information that should not be trusted, resulting in a time-of-check to time-of-use (TOCTOU) flaw. This allows an attacker to have fraudulent activities accepted as valid, leading to a loss of integrity. This issue has been fixed in version 2026.5.4.

## References
- https://github.com/misskey-dev/misskey/releases/tag/2026.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47746.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-38jx-423m-g387
- https://nvd.nist.gov/vuln/detail/CVE-2026-47746

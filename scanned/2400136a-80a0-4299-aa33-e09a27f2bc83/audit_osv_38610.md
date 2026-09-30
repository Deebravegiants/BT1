# [M] Cacti: Package Import Signature Validation Bypass Allows Self-Signed Packages

## Summary
Severity: Medium
Advisory: CVE-2026-40941
Aliases: GHSA-274c-97hj-pv2v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40941
Type: osv

## Details
Cacti is an open source performance and fault management framework. Versions 1.2.30 and prior have a package import signature validation bypass allows which allows self-signed packages. This issue has been fixed in version 1.2.31.

## References
- https://github.com/Cacti/cacti/releases/tag/release%2F1.2.31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40941.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-274c-97hj-pv2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-40941
- https://github.com/Cacti/cacti/pull/7054

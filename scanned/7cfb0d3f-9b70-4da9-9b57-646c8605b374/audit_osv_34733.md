# [C] DataEase DB2 JNDI Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-64428
Aliases: GHSA-88ph-3236-2m2h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-11-20
Source: https://osv.dev/vulnerability/CVE-2025-64428
Type: osv

## Details
Dataease is an open source data visualization analysis tool. Versions prior to 2.10.17 are vulnerable to JNDI injection. A blacklist was added in the patch for version 2.10.14. However, JNDI injection remains possible via the iiop, corbaname, and iiopname schemes. The vulnerability has been fixed in version 2.10.17.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64428.json
- https://github.com/dataease/dataease/security/advisories/GHSA-88ph-3236-2m2h
- https://nvd.nist.gov/vuln/detail/CVE-2025-64428
- https://github.com/dataease/dataease/commit/b7e585c1cc3fc2b73cb289b8680b4b3914be3d53

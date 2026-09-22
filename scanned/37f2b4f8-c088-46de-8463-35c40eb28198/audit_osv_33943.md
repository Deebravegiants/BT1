# [M] Chamilo: PHAR deserialization bypass

## Summary
Severity: Medium
Advisory: CVE-2025-52998
Aliases: GHSA-6mwg-2mw5-rx5v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-52998
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, in the application, deserialization of data is performed, the data can be spoofed. An attacker can create objects of arbitrary classes, as well as fully control their properties, and thus modify the logic of the web application's operation. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52998.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-6mwg-2mw5-rx5v
- https://nvd.nist.gov/vuln/detail/CVE-2025-52998
- https://github.com/chamilo/chamilo-lms/commit/ba7e15d8cfefcd451de939e98d461b17e72eb627

# [M] CVE-2024-10224

## Summary
Severity: Medium
Advisory: CVE-2024-10224
Aliases: GHSA-g597-359q-v529
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-10224
Type: osv

## Details
Qualys discovered that if unsanitized input was used with the library Modules::ScanDeps, before version 1.36 a local attacker could possibly execute arbitrary shell commands by open()ing a "pesky pipe" (such as passing "commands|" as a filename) or by passing arbitrary strings to eval().

## References
- http://seclists.org/fulldisclosure/2024/Nov/15
- http://seclists.org/fulldisclosure/2024/Nov/17
- https://lists.debian.org/debian-lts-announce/2024/11/msg00015.html
- https://www.openwall.com/lists/oss-security/2024/11/19/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10224.json
- https://github.com/rschupp/Module-ScanDeps/security/advisories/GHSA-g597-359q-v529
- https://nvd.nist.gov/vuln/detail/CVE-2024-10224
- https://www.qualys.com/2024/11/19/needrestart/needrestart.txt
- https://www.cve.org/CVERecord?id=CVE-2024-10224
- https://github.com/rschupp/Module-ScanDeps

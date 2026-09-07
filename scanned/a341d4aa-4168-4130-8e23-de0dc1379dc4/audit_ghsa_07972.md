# [M] Moodle TeX formula editor is vulnerable to DoS through lack of execution time limits

## Summary
Severity: Medium
Advisory: GHSA-cg8j-5cr2-568q
CVE: CVE-2026-26047
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-21
Source: https://github.com/advisories/GHSA-cg8j-5cr2-568q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=5.1.0-beta <5.1.2
- Packagist: `moodle/moodle` — affected >=5.0.0-beta <5.0.5
- Packagist: `moodle/moodle` — affected >=0 <4.5.9

## Details
A Denial of Service vulnerability was identified in Moodle’s TeX formula editor. When rendering TeX content using mimetex, insufficient execution time limits could allow specially crafted formulas to consume excessive server resources. An authenticated user could abuse this behavior to degrade performance or cause service interruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26047
- https://github.com/moodle/moodle/commit/8683b4a04939332e353cad1be51222930dc40b2c
- https://access.redhat.com/security/cve/CVE-2026-26047
- https://bugzilla.redhat.com/show_bug.cgi?id=2440905
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=473316

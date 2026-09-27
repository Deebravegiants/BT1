# [H] Path Traversal in io.hawt:project

## Summary
Severity: High
Advisory: GHSA-9g8w-pjpr-prr4
CVE: CVE-2017-2594
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9g8w-pjpr-prr4
Type: github-advisory

## Affected
- Maven: `io.hawt:project` — affected >=0 <1.5.0

## Details
hawtio before versions 2.0-beta-1, 2.0-beta-2, 2.0-m1, 2.0-m2, 2.0-m3, and 1.5 are vulnerable to a path traversal that leads to a NullPointerException with a full stacktrace. An attacker could use this flaw to gather undisclosed information from within hawtio's root.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2594
- https://access.redhat.com/errata/RHSA-2017:1832
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2594

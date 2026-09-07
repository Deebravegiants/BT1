# [C] Policies not properly enforced in OWASP Java HTML Sanitizer

## Summary
Severity: Critical
Advisory: GHSA-3w73-fmf3-hg5c
CVE: CVE-2021-42575
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-3w73-fmf3-hg5c
Type: github-advisory

## Affected
- Maven: `com.googlecode.owasp-java-html-sanitizer:owasp-java-html-sanitizer` — affected >=0 <20211018.1

## Details
The OWASP Java HTML Sanitizer before 20211018.1 does not properly enforce policies associated with the `SELECT`, `STYLE`, and `OPTION` elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42575
- https://docs.google.com/document/d/11SoX296sMS0XoQiQbpxc5pNxSdbJKDJkm5BDv0zrX50
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html

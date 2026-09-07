# [M] Grav is vulnerable to Stored XSS through authenticated user-edited content

## Summary
Severity: Medium
Advisory: GHSA-mh85-44c2-3m97
CVE: CVE-2025-66843
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-15
Source: https://github.com/advisories/GHSA-mh85-44c2-3m97
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0

## Details
grav before v1.7.49.5 has a Stored Cross-Site Scripting (Stored XSS) vulnerability in the page editing functionality. An authenticated low-privileged user with permission to edit content can inject malicious JavaScript payloads into editable fields. The payload is stored on the server and later executed when any other user views or edits the affected page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66843
- https://github.com/Yohane-Mashiro/grav_cve/issues/1
- https://github.com/getgrav/grav

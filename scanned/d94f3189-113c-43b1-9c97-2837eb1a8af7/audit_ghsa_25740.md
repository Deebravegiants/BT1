# [H] Unrestricted Upload of File with Dangerous Type in Croogo

## Summary
Severity: High
Advisory: GHSA-4pww-fqgh-36hj
CVE: CVE-2021-44673
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-4pww-fqgh-36hj
Type: github-advisory

## Affected
- Packagist: `croogo/croogo` — affected >=0

## Details
A Remote Code Execution (RCE) vulnerability exists in Croogo 3.0.2 via admin/file-manager/attachments, which lets a malicious user upload a web shell script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44673
- https://github.com/3erk1n/Vulnerabilities/blob/main/Croogo%203.0.2%20-%20Arbitrary%20File%20Upload-Remote%20Code%20Execution%20(Authenticated).txt
- https://github.com/croogo/croogo

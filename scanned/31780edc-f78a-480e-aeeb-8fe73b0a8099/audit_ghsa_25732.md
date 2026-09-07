# [C] Cross-site Scripting in showdoc/showdoc

## Summary
Severity: Critical
Advisory: GHSA-rphc-h572-2x9f
CVE: CVE-2022-0960
CWE: CWE-434, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-rphc-h572-2x9f
Type: github-advisory

## Affected
- Packagist: `showdoc/showdoc` — affected >=0 <2.10.4

## Details
ShowDoc is a tool greatly applicable for an IT team to share documents online. showdoc/showdoc allows .properties files to upload which lead to stored XSS in versions prior to 2.10.4. This allows attackers to execute malicious scripts in the user's browser. This issue was patched in version 2.10.4. There is currently no known workaround.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0960
- https://github.com/star7th/showdoc/commit/92bc6a83a3a60e01a0d2effb98ab47d8d7eab28f
- https://github.com/star7th/showdoc
- https://huntr.dev/bounties/462cd8a7-b1a9-4e93-af71-b56ba1d7ad4e

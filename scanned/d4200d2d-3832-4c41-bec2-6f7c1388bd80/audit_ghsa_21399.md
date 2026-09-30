# [H] Markdownify subject to Remote Code Execution via malicious markdown file

## Summary
Severity: High
Advisory: GHSA-c942-mfmp-p4fh
CVE: CVE-2022-41709
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-c942-mfmp-p4fh
Type: github-advisory

## Affected
- npm: `electron-markdownify` — affected >=0

## Details
Markdownify version 1.4.1 allows an external attacker to execute arbitrary code remotely on any client attempting to view a malicious markdown file through Markdownify. This is possible because the application has the "nodeIntegration" option enabled. There are currently no patched versions and no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41709
- https://fluidattacks.com/advisories/adams
- https://github.com/amitmerchant1990/electron-markdownify

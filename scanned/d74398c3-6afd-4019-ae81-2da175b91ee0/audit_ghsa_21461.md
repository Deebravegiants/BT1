# [M] Markdownify has Files or Directories Accessible to External Parties

## Summary
Severity: Medium
Advisory: GHSA-qqhf-xfhw-7884
CVE: CVE-2022-41710
CWE: CWE-552
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-04
Source: https://github.com/advisories/GHSA-qqhf-xfhw-7884
Type: github-advisory

## Affected
- npm: `electron-markdownify` — affected >=0

## Details
Markdownify version 1.4.1 allows an external attacker to remotely obtain arbitrary local files on any client that attempts to view a malicious markdown file through Markdownify. This is possible because the application does not have a CSP policy (or at least not strict enough) and/or does not properly validate the contents of markdown files before rendering them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41710
- https://fluidattacks.com/advisories/noisestorm
- https://github.com/amitmerchant1990/electron-markdownify

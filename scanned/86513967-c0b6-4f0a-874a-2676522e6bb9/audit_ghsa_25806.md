# [M] Cross-site Scripting in Fork CMS

## Summary
Severity: Medium
Advisory: GHSA-qf2g-q4mc-w7rr
CVE: CVE-2022-0145
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-25
Source: https://github.com/advisories/GHSA-qf2g-q4mc-w7rr
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.11.1

## Details
Fork CMS prior to 5.11.1 is vulnerable to stored cross-site scripting. When uploading a new module, the description of the module can contain JavaScript code. The JavaScript code may be executed after uploading the new module and looking at the `Details` page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0145
- https://github.com/forkcms/forkcms/commit/981730f1a3d59b423ca903b1f4bf79b848a1766e
- https://github.com/forkcms/forkcms
- https://huntr.dev/bounties/b5b8c680-3cd9-4477-bcd9-3a29657ba7ba

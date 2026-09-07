# [M] Feehi CMS vulnerable to Cross-site Scripting in Username Field

## Summary
Severity: Medium
Advisory: GHSA-v762-47vh-j7q3
CVE: CVE-2020-21146
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v762-47vh-j7q3
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0 <2.0.8.1

## Details
Feehi CMS 2.0.8 is affected by a cross-site scripting (XSS) vulnerability. When the user name is inserted as JavaScript code, browsing the post will trigger the XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21146
- https://github.com/liufee/cms/issues/43
- https://github.com/liufee/cms/commit/e92f6877d96e53498101d0664174956e94223d6e
- https://github.com/liufee/cms

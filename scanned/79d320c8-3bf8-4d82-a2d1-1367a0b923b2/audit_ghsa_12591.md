# [C] liufee CMS File Upload vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q3q5-qvh5-cmw5
CVE: CVE-2020-21174
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-q3q5-qvh5-cmw5
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0 <2.0.8.1

## Details
File Upload vulnerability in liufee CMS v.2.0.7.1 allows a remote attacker to execute arbitrary code via the image suffix function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-21174
- https://github.com/liufee/cms/issues/44
- https://github.com/liufee/cms/commit/ecbfb0ca77874ead5b6e79b96a5e1f94e67475a9
- https://github.com/liufee/cms

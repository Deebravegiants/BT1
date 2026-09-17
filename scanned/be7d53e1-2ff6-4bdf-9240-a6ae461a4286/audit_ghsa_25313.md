# [M] Fastly Magento2 sensitive information disclosure

## Summary
Severity: Medium
Advisory: GHSA-vpq9-c67q-23fq
CVE: CVE-2017-13761
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vpq9-c67q-23fq
Type: github-advisory

## Affected
- Packagist: `fastly/magento2` — affected >=0 <1.2.26

## Details
The Fastly CDN module before 1.2.26 for Magento2, when used with a third-party authentication plugin, might allow remote authenticated users to obtain sensitive information from authenticated sessions via vectors involving caching of redirect responses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-13761
- https://www.fastly.com/security-advisories/vulnerability-fastly-open-source-cdn-module-intended-be-integrated-magento2

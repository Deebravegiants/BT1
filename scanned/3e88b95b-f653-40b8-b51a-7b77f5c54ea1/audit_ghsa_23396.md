# [M] Yii Incorrectly Implements CORS

## Summary
Severity: Medium
Advisory: GHSA-cr6r-6xm9-ww22
CVE: CVE-2018-20745
CWE: CWE-346
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cr6r-6xm9-ww22
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2` — affected >=0 <2.0.16

## Details
Yii 2.x through 2.0.15.1 actively converts a wildcard CORS policy into reflecting an arbitrary Origin header value, which is incompatible with the CORS security design, and could lead to CORS misconfiguration security problems.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20745
- https://github.com/yiisoft/yii2/issues/16193
- https://github.com/yiisoft/yii2/pull/16198
- https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-chen.pdf

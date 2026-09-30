# [H] Unsafe deserialization in SmtpTransport in CakePHP

## Summary
Severity: High
Advisory: GHSA-qhrx-hcm6-pmrw
CVE: CVE-2019-11458
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-qhrx-hcm6-pmrw
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=3.0.0 <3.5.18
- Packagist: `cakephp/cakephp` — affected >=3.6.0 <3.6.15
- Packagist: `cakephp/cakephp` — affected >=3.7.0 <3.7.7

## Details
An issue was discovered in SmtpTransport in CakePHP 3.7.6. An unserialized object with modified internal properties can trigger arbitrary file overwriting upon destruction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11458
- https://github.com/cakephp/cakephp/commit/1a74e798309192a9895c9cedabd714ceee345f4e
- https://github.com/cakephp/cakephp/commit/81412fbe2cb88a304dbeeece1955bc0aec98edb1
- https://github.com/cakephp/cakephp/commit/c25b91bf7c72db43c01b47a634fd02112ff9f1cd
- https://bakery.cakephp.org/2019/04/23/cakephp_377_3615_3518_released.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/cakephp/cakephp/CVE-2019-11458.yaml
- https://github.com/cakephp/cakephp
- https://github.com/cakephp/cakephp/commits/master
- https://github.com/cakephp/cakephp/compare/3.7.6...3.7.7
- https://github.com/cakephp/cakephp/releases

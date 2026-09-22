# [H] ReDoS issue in dparse

## Summary
Severity: High
Advisory: GHSA-8fg9-p83m-x5pq
CVE: CVE-2022-39280
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-8fg9-p83m-x5pq
Type: github-advisory

## Affected
- PyPI: `dparse` — affected >=0 <0.5.2

## Details
### Impact
dparse versions prior to 0.5.1 contain a regular expression that is vulnerable to [ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (Regular Expression Denial of Service).

All users parsing index server URLs with dparse are impacted by this vulnerability.

### Patches
The Patch is applied in the `0.5.2` version, all users are recommended to upgrade as soon as possible.

### Workarounds
Avoid passing index server URLs in the source file to be parsed.

### References
[https://github.com/pyupio/dparse/tree/security/remove-intensive-regex](https://github.com/pyupio/dparse/tree/security/remove-intensive-regex)

### For more information
If you have any questions or comments about this advisory:
* Email us at [support@pyup.io](mailto:support@pyup.io)

## References
- https://github.com/pyupio/dparse/security/advisories/GHSA-8fg9-p83m-x5pq
- https://nvd.nist.gov/vuln/detail/CVE-2022-39280
- https://github.com/pyupio/dparse/commit/8c990170bbd6c0cf212f1151e9025486556062d5
- https://github.com/pyupio/dparse/commit/d87364f9db9ab916451b1b036cfeb039e726e614
- https://github.com/pypa/advisory-database/tree/main/vulns/dparse/PYSEC-2022-301.yaml
- https://github.com/pyupio/dparse
- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS

# [H] Name confusion in x509 Subject Alternative Name fields

## Summary
Severity: High
Advisory: GHSA-ff7q-6vwh-v9m4
CVE: CVE-2023-52892
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-28
Source: https://github.com/advisories/GHSA-ff7q-6vwh-v9m4
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=0 <1.0.22
- Packagist: `phpseclib/phpseclib` — affected >=2.0.0 <2.0.46
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.33

## Details
In phpseclib before 1.0.22, 2.x before 2.0.46, and 3.x before 3.0.33, some characters in Subject Alternative Name fields in TLS certificates are incorrectly allowed to have a special meaning in regular expressions (such as a + wildcard), leading to name confusion in X.509 certificate host verification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52892
- https://github.com/phpseclib/phpseclib/issues/1943
- https://github.com/phpseclib/phpseclib/commit/6cd6e8ceab9f2b55c8cd81d2192bf98cbeaf4627
- https://github.com/phpseclib/phpseclib
- https://github.com/phpseclib/phpseclib/releases/tag/3.0.33
- https://github.com/x509-name-testing/name_testing_artifacts

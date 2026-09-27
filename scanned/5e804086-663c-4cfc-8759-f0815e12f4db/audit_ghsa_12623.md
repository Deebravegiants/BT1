# [M] Whaleal IceFrog is vulnerable to deserialization 

## Summary
Severity: Medium
Advisory: GHSA-rx62-5cw6-x29q
CVE: CVE-2023-3308
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-18
Source: https://github.com/advisories/GHSA-rx62-5cw6-x29q
Type: github-advisory

## Affected
- Maven: `com.whaleal.icefrog:icefrog-all` — affected >=0

## Details
Whaleal IceFrog v1.1.8 component Aviator Template Engine is vulnerable to deserialization of untrusted data. The application deserializes untrusted data without sufficiently verifying that the resulting data will be valid.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3308
- https://github.com/NanKeXXX/selfVuln_poc/blob/main/whaleal%3Aicefrog/icefrog_1.1.8_RCE.md
- https://github.com/NanKeXXX/selfVuln_poc/blob/main/whaleal:icefrog/icefrog_1.1.8_RCE.md
- https://github.com/whaleal/icefrog
- https://vuldb.com/?ctiid.231804
- https://vuldb.com/?id.231804

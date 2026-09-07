# [C] Solon vulnerable to deserialization of untrusted data

## Summary
Severity: Critical
Advisory: GHSA-7q8c-49f4-4c8q
CVE: CVE-2023-35839
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-19
Source: https://github.com/advisories/GHSA-7q8c-49f4-4c8q
Type: github-advisory

## Affected
- Maven: `org.noear:solon` — affected >=0 <2.3.3

## Details
A bypass in the component sofa-hessian of Solon before v2.3.3 allows attackers to execute arbitrary code via providing crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35839
- https://github.com/noear/solon/issues/145
- https://github.com/noear/solon
- https://github.com/noear/solon/compare/v2.3.2...v2.3.3

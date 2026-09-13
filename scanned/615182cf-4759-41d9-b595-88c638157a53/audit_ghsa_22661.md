# [H] gopkg.in/yaml.v3 Denial of Service

## Summary
Severity: High
Advisory: GHSA-hp87-p4gw-j4gq
CVE: CVE-2022-28948
CWE: CWE-502
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-20
Source: https://github.com/advisories/GHSA-hp87-p4gw-j4gq
Type: github-advisory

## Affected
- Go: `gopkg.in/yaml.v3` — affected >=0 <3.0.1

## Details
An issue in the Unmarshal function in Go-Yaml v3 can cause a program to panic when attempting to deserialize invalid input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28948
- https://github.com/go-yaml/yaml/issues/665
- https://github.com/go-yaml/yaml/issues/666
- https://github.com/go-yaml/yaml/commit/8f96da9f5d5eff988554c1aae1784627c4bf6754
- https://github.com/go-yaml/yaml/commit/f6f7691b1fdeb513f56608cd2c32c51f8194bf51
- https://github.com/go-yaml/yaml
- https://security.netapp.com/advisory/ntap-20220923-0006

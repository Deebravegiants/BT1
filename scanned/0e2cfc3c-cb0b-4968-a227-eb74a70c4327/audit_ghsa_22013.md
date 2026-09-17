# [H] Out of bounds read in json-smart

## Summary
Severity: High
Advisory: GHSA-fg2v-w576-w4v3
CVE: CVE-2021-31684
CWE: CWE-125, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-fg2v-w576-w4v3
Type: github-advisory

## Affected
- Maven: `net.minidev:json-smart` — affected >=1.3.0 <1.3.3
- Maven: `net.minidev:json-smart` — affected >=2.4.0 <2.4.4

## Details
A vulnerability was discovered in the indexOf function of JSONParserByteArray in JSON Smart versions prior to 1.3.3 and 2.4.5 which causes a denial of service (DOS) via a crafted web request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31684
- https://github.com/netplex/json-smart-v1/issues/10
- https://github.com/netplex/json-smart-v2/issues/67
- https://github.com/netplex/json-smart-v1/pull/11
- https://github.com/netplex/json-smart-v2/pull/68
- https://github.com/netplex/json-smart-v1
- https://lists.debian.org/debian-lts-announce/2023/03/msg00030.html
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html

# [H] ldap3_proto has LDAP Filter stack exhaustion

## Summary
Severity: High
Advisory: GHSA-qcxq-75wr-5cm8
CWE: CWE-674, CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-qcxq-75wr-5cm8
Type: github-advisory

## Affected
- crates.io: `ldap3_proto` — affected >=0 <0.7.1

## Details
### Impact
LDAP queries are not validated for depth, which can cause the parser (both PEG and ASN) to exhaust the stack. This *may* cause a denial of service in applications that process queries.

### Workarounds
N/A

### References
Related to GHSA-r5fr-9gmv-jggh

## References
- https://github.com/kanidm/ldap3/security/advisories/GHSA-qcxq-75wr-5cm8
- https://github.com/advisories/GHSA-r5fr-9gmv-jggh
- https://github.com/kanidm/ldap3

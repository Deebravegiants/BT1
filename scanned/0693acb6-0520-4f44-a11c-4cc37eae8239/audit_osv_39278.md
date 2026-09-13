# [H] SAML Authentication Replay in Rancher

## Summary
Severity: High
Advisory: CVE-2026-44946
Aliases: GHSA-c5jm-xcmq-9j95
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-44946
Type: osv

## Details
A SAML authentication replay vulnerability in Rancher's Assertion
 Consumer Service (ACS) handler did not enforce 
one-time use of SAML assertion, potentially allowing person in the middle attacks against Rancher, affecting Rancher 2.14.0 before 2.14.3,

## References
- https://github.com/rancher/rancher/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44946.json
- https://github.com/rancher/rancher/security/advisories/GHSA-c5jm-xcmq-9j95
- https://nvd.nist.gov/vuln/detail/CVE-2026-44946

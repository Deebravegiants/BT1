# [M] Privilege Escalation in Cloud Native Computing Foundation Harbor

## Summary
Severity: Medium
Advisory: GHSA-q6cj-6jvq-jwmh
CVE: CVE-2019-19023
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-q6cj-6jvq-jwmh
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.7.0 <1.8.6
- Go: `github.com/goharbor/harbor` — affected >=1.9.0 <1.9.3

## Details
Cloud Native Computing Foundation Harbor prior to 1.8.6 and 1.9.3 has a Privilege Escalation Vulnerability in the VMware Harbor Container Registry for the Pivotal Platform.

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-3868-7c5x-4827
- https://nvd.nist.gov/vuln/detail/CVE-2019-19023
- https://github.com/goharbor/harbor/security/advisories
- https://tanzu.vmware.com/security/cve-2019-19023

# [M] Stale PSA ClusterRoleBinding Persists After RoleTemplate Downgrade in Rancher

## Summary
Severity: Medium
Advisory: CVE-2026-44947
Aliases: GHSA-c4rp-wgqc-mfhc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-44947
Type: osv

## Details
A missing clean-up in the legacy Project Role Template Binding (PRTB) 
reconciler in Rancher versions 2.13.0 up to 2.13.7 and 2.14.0 up to 2.14.3 allowed users to retain unauthorized Pod Security 
Admission (PSA) permissions after an administrator removes those 
permissions from a RoleTemplate.

## References
- https://github.com/rancher/rancher/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44947.json
- https://github.com/rancher/rancher/security/advisories/GHSA-c4rp-wgqc-mfhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44947

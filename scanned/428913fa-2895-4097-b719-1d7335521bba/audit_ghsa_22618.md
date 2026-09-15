# [H] Rancher Project Members Have Continued Access to Namespaces After Being Removed From Them

## Summary
Severity: High
Advisory: GHSA-6r7x-4q7g-h83j
CVE: CVE-2019-6287
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6r7x-4q7g-h83j
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.1.6

## Details
In Rancher 2.0.0 through 2.1.5, project members have continued access to create, update, read, and delete namespaces in a project after they have been removed from it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6287
- https://github.com/rancher/rancher/issues/17244
- https://github.com/rancher/rancher/issues/17724
- https://forums.rancher.com/t/rancher-release-v2-1-6/13148
- https://forums.rancher.com/t/rancher-security-announcement-cve-2018-20321-and-cve-2019-6287/13149
- https://github.com/rancher/rancher
- https://rancher.com/blog/2019/2019-01-29-explaining-security-vulnerabilities-addressed-in-rancher-v2-1-6-and-v2-0-11

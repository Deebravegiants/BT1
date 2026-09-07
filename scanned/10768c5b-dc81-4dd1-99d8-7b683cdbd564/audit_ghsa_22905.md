# [H] Rancher code injection via fluentd config commands

## Summary
Severity: High
Advisory: GHSA-53pj-67m4-9w98
CVE: CVE-2019-12303
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-53pj-67m4-9w98
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.0.0 <2.2.4

## Details
In Rancher 2 through 2.2.3, Project owners can inject additional fluentd configuration to read files or execute arbitrary commands inside the fluentd container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12303
- https://forums.rancher.com/t/rancher-release-v2-2-4-addresses-rancher-cve-2019-12274-and-cve-2019-12303/14466
- https://github.com/rancher/rancher

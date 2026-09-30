# [H] kube-apiserver authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-92hx-3mh6-hc49
CVE: CVE-2023-1260
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-24
Source: https://github.com/advisories/GHSA-92hx-3mh6-hc49
Type: github-advisory

## Affected
- Go: `github.com/openshift/apiserver-library-go` — affected >=0 <0.0.0-20230621

## Details
An authentication bypass vulnerability was discovered in kube-apiserver. This issue could allow a remote, authenticated attacker who has been given permissions "update, patch" the "pods/ephemeralcontainers" subresource beyond what the default is. They would then need to create a new pod or patch one that they already have access to. This might allow evasion of SCC admission restrictions, thereby gaining control of a privileged pod.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1260
- https://github.com/openshift/apiserver-library-go/commit/a994128188486d2dce99a528fbcc017d276081e0
- https://access.redhat.com/errata/RHSA-2023:3976
- https://access.redhat.com/errata/RHSA-2023:4093
- https://access.redhat.com/errata/RHSA-2023:4312
- https://access.redhat.com/errata/RHSA-2023:4898
- https://access.redhat.com/errata/RHSA-2023:5008
- https://access.redhat.com/security/cve/CVE-2023-1260
- https://bugzilla.redhat.com/show_bug.cgi?id=2176267
- https://github.com/advisories/GHSA-92hx-3mh6-hc49
- https://github.com/openshift/apiserver-library-go
- https://security.netapp.com/advisory/ntap-20231020-0010

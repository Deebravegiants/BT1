# [H] containernetworking/cni improper limitation of path name

## Summary
Severity: High
Advisory: GHSA-xjqr-g762-pxwp
CVE: CVE-2021-20206
CWE: CWE-20, CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-xjqr-g762-pxwp
Type: github-advisory

## Affected
- Go: `github.com/containernetworking/cni` — affected >=0 <0.8.1

## Details
An improper limitation of path name flaw was found in containernetworking/cni in versions before 0.8.1. When specifying the plugin to load in the 'type' field in the network configuration, it is possible to use special elements such as "../" separators to reference binaries elsewhere on the system. This flaw allows an attacker to execute other existing binaries other than the cni plugins/types, such as 'reboot'. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.
### Specific Go Packages Affected
github.com/containernetworking/cni/pkg/invoke

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20206
- https://github.com/containernetworking/cni/pull/808
- https://bugzilla.redhat.com/show_bug.cgi?id=1919391
- https://github.com/containernetworking/cni
- https://pkg.go.dev/vuln/GO-2022-0230
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMCONTAINERNETWORKINGCNIPKGINVOKE-1070549

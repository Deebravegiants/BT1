# [M] kube-state-metrics may expose secret content in metrics

## Summary
Severity: Medium
Advisory: GHSA-c92w-72c5-9x59
CVE: CVE-2019-10223
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c92w-72c5-9x59
Type: github-advisory

## Affected
- Go: `k8s.io/kube-state-metrics` — affected >=1.7.0 <1.7.2

## Details
A security issue was discovered in the kube-state-metrics versions v1.7.0 and v1.7.1. An experimental feature was added to the v1.7.0 release that enabled annotations to be exposed as metrics. By default, the kube-state-metrics metrics only expose metadata about Secrets. However, a combination of the default `kubectl` behavior and this new feature can cause the entire secret content to end up in metric labels thus inadvertently exposing the secret content in metrics. This feature has been reverted and released as the v1.7.2 release. If you are running the v1.7.0 or v1.7.1 release, please upgrade to the v1.7.2 release as soon as possible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10223
- https://github.com/kubernetes/kube-state-metrics/commit/03122fe3e2df49a9a7298b8af921d3c37c430f7f
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10223
- https://github.com/kubernetes/kube-state-metrics
- https://github.com/kubernetes/kube-state-metrics/releases/tag/v1.7.2
- https://pkg.go.dev/vuln/GO-2022-0621
- https://www.openwall.com/lists/oss-security/2019/08/09/1
- http://www.openwall.com/lists/oss-security/2019/08/15/8

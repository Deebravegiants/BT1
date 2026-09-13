# [M] github.com/openshift/apiserver-library-go Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5465-xc2j-6p84
CVE: CVE-2023-0229
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-5465-xc2j-6p84
Type: github-advisory

## Affected
- Go: `github.com/openshift/apiserver-library-go` — affected >=0 <0.0.0-20230120221150-cefee9e0162b

## Details
A flaw was found in github.com/openshift/apiserver-library-go, used in OpenShift 4.12 and 4.11, that contains an issue that can allow low-privileged users to set the seccomp profile for pods they control to "unconfined." By default, the seccomp profile used in the restricted-v2 Security Context Constraint (SCC) is "runtime/default," allowing users to disable seccomp for pods they can create and modify.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0229
- https://github.com/openshift/apiserver-library-go/pull/97
- https://github.com/openshift/apiserver-library-go/commit/30f75d79e424ca462c6de53ee8b93f91183763e6
- https://bugzilla.redhat.com/show_bug.cgi?id=2160349
- github.com/openshift/apiserver-library-go

# [M] golang.org/x/crypto vulnerable to invoking bypass of certificate restrictions

## Summary
Severity: Medium
Advisory: GHSA-45gg-vh54-h5m9
CVE: CVE-2026-39828
CWE: CWE-281, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-45gg-vh54-h5m9
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
When an SSH server authentication callback returned PartialSuccessError with non-nil Permissions, those permissions were silently discarded, potentially dropping certificate restrictions such as force-command after a second factor succeeded. Returning non-nil Permissions with PartialSuccessError now results in a connection error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39828
- https://access.redhat.com/errata/RHSA-2026:40119
- https://access.redhat.com/errata/RHSA-2026:40262
- https://access.redhat.com/errata/RHSA-2026:40945
- https://access.redhat.com/errata/RHSA-2026:40969
- https://access.redhat.com/errata/RHSA-2026:40972
- https://access.redhat.com/errata/RHSA-2026:40974
- https://access.redhat.com/errata/RHSA-2026:41019
- https://access.redhat.com/errata/RHSA-2026:41031
- https://access.redhat.com/errata/RHSA-2026:41036
- https://access.redhat.com/errata/RHSA-2026:41055
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/security/cve/CVE-2026-39828
- https://bugzilla.redhat.com/show_bug.cgi?id=2480687
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/781621
- https://go.dev/issue/79562
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5014
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-39828.json

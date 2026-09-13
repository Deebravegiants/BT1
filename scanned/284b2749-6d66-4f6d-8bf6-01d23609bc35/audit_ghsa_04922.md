# [C] golang.org/x/crypto doesn't drop invoking agent constraints when forwarding keys

## Summary
Severity: Critical
Advisory: GHSA-f5wc-c3c7-36mc
CVE: CVE-2026-39832
CWE: CWE-281, CWE-502
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-f5wc-c3c7-36mc
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
When adding a key to a remote agent constraint extensions such as restrict-destination-v00@openssh.com were not serialized in the request. Destination restrictions were silently stripped when forwarding keys, allowing unrestricted use of the key on the remote host. The client now serializes all constraint extensions. Additionally, the in-memory keyring returned by NewKeyring() now rejects keys with unsupported constraint extensions instead of silently ignoring them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39832
- https://access.redhat.com/errata/RHSA-2026:35833
- https://access.redhat.com/errata/RHSA-2026:41036
- https://access.redhat.com/errata/RHSA-2026:41066
- https://access.redhat.com/errata/RHSA-2026:42146
- https://access.redhat.com/errata/RHSA-2026:42796
- https://access.redhat.com/errata/RHSA-2026:43052
- https://access.redhat.com/errata/RHSA-2026:43692
- https://access.redhat.com/errata/RHSA-2026:49944
- https://access.redhat.com/errata/RHSA-2026:52857
- https://access.redhat.com/errata/RHSA-2026:52910
- https://access.redhat.com/security/cve/CVE-2026-39832
- https://bugzilla.redhat.com/show_bug.cgi?id=2480685
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/778642
- https://go.dev/issue/79435
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5006
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-39832.json
- https://access.redhat.com/errata/RHSA-2026:36199

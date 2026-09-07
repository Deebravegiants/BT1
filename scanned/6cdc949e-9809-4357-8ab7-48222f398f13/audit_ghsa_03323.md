# [H] Path Traversal in Buildah

## Summary
Severity: High
Advisory: GHSA-fx8w-mjvm-hvpc
CVE: CVE-2020-10696
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-fx8w-mjvm-hvpc
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=0 <1.14.4

## Details
A path traversal flaw was found in Buildah in versions before 1.14.5. This flaw allows an attacker to trick a user into building a malicious container image hosted on an HTTP(s) server and then write files to the user's system anywhere that the user has permissions.

### Specific Go Packages Affected
github.com/containers/buildah/imagebuildah

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10696
- https://github.com/containers/buildah/pull/2245
- https://access.redhat.com/security/cve/cve-2020-10696
- https://bugzilla.redhat.com/show_bug.cgi?id=1817651
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10696
- https://github.com/containers/buildah
- https://pkg.go.dev/vuln/GO-2022-0828

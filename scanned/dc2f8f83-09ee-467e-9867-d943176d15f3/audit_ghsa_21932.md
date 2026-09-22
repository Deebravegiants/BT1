# [M] containers/image library Insufficiently Protects Credentials

## Summary
Severity: Medium
Advisory: GHSA-85p9-j7c9-v4gr
CVE: CVE-2019-10214
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-85p9-j7c9-v4gr
Type: github-advisory

## Affected
- Go: `github.com/containers/image` — affected >=0 <3.0.0

## Details
The containers/image library used by the container tools Podman, Buildah, and Skopeo in Red Hat Enterprise Linux version 8 and CRI-O in OpenShift Container Platform, does not enforce TLS connections to the container registry authorization service. An attacker could use this vulnerability to launch a MiTM attack and steal login credentials or bearer tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10214
- https://github.com/containers/image/issues/654
- https://github.com/containers/image/pull/655
- https://github.com/containers/image/pull/669
- https://github.com/containers/image/commit/634605d06e738aec8332bcfd69162e7509ac7aaf
- https://bugzilla.redhat.com/show_bug.cgi?id=1732508
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10214
- https://github.com/containers/image
- https://pkg.go.dev/vuln/GO-2021-0081
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00041.html

# [M] Buildah allows arbitrary directory mount

## Summary
Severity: Medium
Advisory: GHSA-586p-749j-fhwp
CVE: CVE-2024-9675
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-09
Source: https://github.com/advisories/GHSA-586p-749j-fhwp
Type: github-advisory

## Affected
- Go: `github.com/containers/buildah` — affected >=0 <1.38.0

## Details
A vulnerability was found in Buildah. Cache mounts do not properly validate that user-specified paths for the cache are within our cache directory, allowing a `RUN` instruction in a Container file to mount an arbitrary directory from the host (read/write) into the container as long as those files can be accessed by the user running Buildah.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9675
- https://github.com/containers/buildah/commit/aa67e5d71ee7ec07122a210baa3b13966a9e086c
- https://pkg.go.dev/vuln/GO-2024-3186
- https://github.com/containers/buildah
- https://bugzilla.redhat.com/show_bug.cgi?id=2317458
- https://access.redhat.com/security/cve/CVE-2024-9675
- https://access.redhat.com/errata/RHSA-2025:3573
- https://access.redhat.com/errata/RHSA-2025:3301
- https://access.redhat.com/errata/RHSA-2025:2710
- https://access.redhat.com/errata/RHSA-2025:2701
- https://access.redhat.com/errata/RHSA-2025:2454
- https://access.redhat.com/errata/RHSA-2025:2449
- https://access.redhat.com/errata/RHSA-2025:2445
- https://access.redhat.com/errata/RHSA-2024:9459
- https://access.redhat.com/errata/RHSA-2024:9454
- https://access.redhat.com/errata/RHSA-2024:9051
- https://access.redhat.com/errata/RHSA-2024:8994
- https://access.redhat.com/errata/RHSA-2024:8984
- https://access.redhat.com/errata/RHSA-2024:8846
- https://access.redhat.com/errata/RHSA-2024:8709

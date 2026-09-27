# [H] Docker Registry has Allocation of Resources Without Limits or Throttling

## Summary
Severity: High
Advisory: GHSA-h62f-wm92-2cmw
CVE: CVE-2017-11468
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h62f-wm92-2cmw
Type: github-advisory

## Affected
- Go: `github.com/docker/distribution` — affected >=0 <2.7.0-rc.0

## Details
Docker Registry before 2.6.2 in Docker Distribution does not properly restrict the amount of content accepted from a user, which allows remote attackers to cause a denial of service (memory consumption) via the manifest endpoint.
### Specific Go Packages Affected
github.com/docker/distribution/registry/storage
github.com/docker/distribution/registry/handlers

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11468
- https://github.com/distribution/distribution/pull/2340
- https://github.com/docker/distribution/pull/2340
- https://github.com/distribution/distribution/commit/91c507a39abfce14b5c8541cf284330e22208c0f
- https://access.redhat.com/errata/RHSA-2017:2603
- https://github.com/distribution/distribution
- https://github.com/docker/distribution/releases/tag/v2.6.2
- https://pkg.go.dev/vuln/GO-2021-0072
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00047.html

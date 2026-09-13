# [H] Podman Elevated Container Privileges

## Summary
Severity: High
Advisory: GHSA-wp7w-vx86-vj9h
CVE: CVE-2018-10856
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wp7w-vx86-vj9h
Type: github-advisory

## Affected
- Go: `github.com/containers/podman` — affected >=0 <0.6.1

## Details
It has been discovered that podman before version 0.6.1 does not drop capabilities when executing a container as a non-root user. This results in unnecessary privileges being granted to the container.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10856
- https://github.com/projectatomic/libpod/commit/bae80a0b663925ec751ad2784ca32989403cdc24
- https://access.redhat.com/errata/RHSA-2018:2037
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10856
- https://github.com/containers/podman

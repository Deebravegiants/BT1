# [M] Docker Moby /proc/scsi Path Exposure Allows Host Data Loss (SCSI MICDROP)

## Summary
Severity: Medium
Advisory: GHSA-vfjc-2qcw-j95j
CVE: CVE-2017-16539
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vfjc-2qcw-j95j
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <17.12.0-ce

## Details
The DefaultLinuxSpec function in oci/defaults.go in Docker Moby through 17.03.2-ce does not block /proc/scsi pathnames, which allows attackers to trigger data loss (when certain older Linux kernels are used) by leveraging Docker container access to write a "scsi remove-single-device" line to /proc/scsi/scsi, aka SCSI MICDROP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16539
- https://github.com/moby/moby/pull/35399
- https://github.com/moby/moby/commit/a21ecdf3c8a343a7c94e4c4d01b178c87ca7aaa1
- https://github.com/moby/moby
- https://marc.info/?l=linux-scsi&m=150985062200941&w=2
- https://marc.info/?l=linux-scsi&m=150985455801444&w=2
- https://twitter.com/ewindisch/status/926443521820774401

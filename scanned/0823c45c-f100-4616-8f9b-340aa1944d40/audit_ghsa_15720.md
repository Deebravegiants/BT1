# [M] snapd failed to properly check the file type when extracting a snap

## Summary
Severity: Medium
Advisory: GHSA-64jh-cjwc-w8q6
CVE: CVE-2024-29068
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-07-25
Source: https://github.com/advisories/GHSA-64jh-cjwc-w8q6
Type: github-advisory

## Affected
- Go: `github.com/snapcore/snapd` — affected >=0 <2.62

## Details
In snapd versions prior to 2.62, snapd failed to properly check the file type when extracting a snap. The snap format is a squashfs file-system image and so can contain files that are non-regular files (such as pipes or sockets etc). Various file entries within the snap squashfs image (such as icons etc) are directly read by snapd when it is extracted. An attacker who could convince a user to install a malicious snap which contained non-regular files at these paths could then cause snapd to block indefinitely trying to read from such files and cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29068
- https://github.com/snapcore/snapd/pull/13682
- https://github.com/snapcore/snapd/commit/b66fee81606a1c05f965a876ccbaf44174194063
- https://github.com/snapcore/snapd
- https://pkg.go.dev/vuln/GO-2024-3008

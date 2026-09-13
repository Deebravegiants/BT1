# [M] CVE-2017-8934

## Summary
Severity: Medium
Advisory: CVE-2017-8934
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-15
Source: https://osv.dev/vulnerability/CVE-2017-8934
Type: osv

## Details
PCManFM 1.2.5 insecurely uses /tmp for a socket file, allowing a local user to cause a denial of service (application unavailability).

## References
- https://git.lxde.org/gitweb/?p=lxde/pcmanfm.git%3Ba=commit%3Bh=bc8c3d871e9ecc67c47ff002b68cf049793faf08
- https://bugs.debian.org/862571

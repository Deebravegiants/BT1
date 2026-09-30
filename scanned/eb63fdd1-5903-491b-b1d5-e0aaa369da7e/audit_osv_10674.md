# [M] CVE-2017-18188

## Summary
Severity: Medium
Advisory: CVE-2017-18188
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/CVE-2017-18188
Type: osv

## Details
OpenRC opentmpfiles through 0.1.3, when the fs.protected_hardlinks sysctl is turned off, allows local users to obtain ownership of arbitrary files by creating a hard link inside a directory on which "chown -R" will be run.

## References
- https://github.com/OpenRC/opentmpfiles/issues/3

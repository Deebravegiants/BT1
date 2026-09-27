# [M] CVE-2018-21269

## Summary
Severity: Medium
Advisory: CVE-2018-21269
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-10-27
Source: https://osv.dev/vulnerability/CVE-2018-21269
Type: osv

## Details
checkpath in OpenRC through 0.42.1 might allow local users to take ownership of arbitrary files because a non-terminal path component can be a symlink.

## References
- https://github.com/OpenRC/openrc/issues/201

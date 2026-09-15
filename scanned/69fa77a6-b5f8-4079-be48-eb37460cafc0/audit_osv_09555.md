# [M] CVE-2017-1000141

## Summary
Severity: Medium
Advisory: CVE-2017-1000141
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2018-01-30
Source: https://osv.dev/vulnerability/CVE-2017-1000141
Type: osv

## Details
An issue was discovered in Mahara before 18.10.0. It mishandled user requests that could discontinue a user's ability to maintain their own account (changing username, changing primary email address, deleting account). The correct behavior was to either prompt them for their password and/or send a warning to their primary email address.

## References
- https://bugs.launchpad.net/mahara/+bug/1422492

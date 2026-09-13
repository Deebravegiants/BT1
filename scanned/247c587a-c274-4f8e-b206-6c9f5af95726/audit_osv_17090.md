# [M] CVE-2020-12135

## Summary
Severity: Medium
Advisory: CVE-2020-12135
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-04-24
Source: https://osv.dev/vulnerability/CVE-2020-12135
Type: osv

## Details
bson before 0.8 incorrectly uses int rather than size_t for many variables, parameters, and return values. In particular, the bson_ensure_space() parameter bytesNeeded could have an integer overflow via properly constructed bson input.

## References
- https://usn.ubuntu.com/4450-1/
- https://github.com/10gen-archive/mongo-c-driver-legacy/commit/1a1f5e26a4309480d88598913f9eebf9e9cba8ca#diff-f7d29a680148f52d6601f59ed787f577
- https://launchpadlibrarian.net/474887364/bson-fix-overflow.patch
- https://bugs.launchpad.net/ubuntu/+source/whoopsie/+bug/1872560

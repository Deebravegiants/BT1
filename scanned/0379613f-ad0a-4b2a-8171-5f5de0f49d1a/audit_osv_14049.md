# [H] CVE-2018-6574

## Summary
Severity: High
Advisory: CVE-2018-6574
Aliases: GO-2022-0201
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2018-6574
Type: osv

## Details
Go before 1.8.7, Go 1.9.x before 1.9.4, and Go 1.10 pre-releases before Go 1.10rc2 allow "go get" remote command execution during source code build, by leveraging the gcc or clang plugin feature, because -fplugin= and -plugin= arguments were not blocked.

## References
- https://groups.google.com/forum/#%21topic/golang-nuts/Gbhh1NxAjMU
- https://groups.google.com/forum/#%21topic/golang-nuts/sprOaQ5m3Dk
- https://access.redhat.com/errata/RHSA-2018:0878
- https://access.redhat.com/errata/RHSA-2018:1304
- https://www.debian.org/security/2019/dsa-4380
- https://github.com/golang/go/issues/23672
- https://github.com/KINGSABRI/CVE-in-Ruby/tree/master/CVE-2018-6574

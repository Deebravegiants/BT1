# [C] CVE-2019-17545

## Summary
Severity: Critical
Advisory: CVE-2019-17545
Aliases: PYSEC-2019-241
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/CVE-2019-17545
Type: osv

## Details
GDAL through 3.0.1 has a poolDestroy double free in OGRExpatRealloc in ogr/ogr_expat.cpp when the 10MB threshold is exceeded.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CB7RRPCQP253XA5MYUOLHLRPKNGKVZNT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XVRC3EBQBFBVQC26XJE3AI3KQXC2NGTP/
- https://lists.debian.org/debian-lts-announce/2019/11/msg00005.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00040.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=16178
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00022.html
- https://github.com/OSGeo/gdal/commit/148115fcc40f1651a5d15fa34c9a8c528e7147bb

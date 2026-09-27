# [H] CVE-2020-12762

## Summary
Severity: High
Advisory: CVE-2020-12762
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/CVE-2020-12762
Type: osv

## Details
json-c through 0.14 has an integer overflow and out-of-bounds write via a large JSON file, as demonstrated by printbuf_memappend.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBR36IXYBHITAZFB5PFBJTED22WO5ONB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CQQRRGBQCAWNCCJ2HN3W5SSCZ4QGMXQI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W226TSCJBEOXDUFVKNWNH7ETG7AR6MCS/
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
- https://lists.debian.org/debian-lts-announce/2020/05/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00034.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00031.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00023.html
- https://security.gentoo.org/glsa/202006-13
- https://security.netapp.com/advisory/ntap-20210521-0001/
- https://usn.ubuntu.com/4360-1/
- https://usn.ubuntu.com/4360-4/
- https://www.debian.org/security/2020/dsa-4741
- https://github.com/json-c/json-c/pull/592
- https://github.com/rsyslog/libfastjson/issues/161

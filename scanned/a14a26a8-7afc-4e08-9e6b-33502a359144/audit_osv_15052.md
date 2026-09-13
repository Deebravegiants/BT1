# [M] CVE-2019-13114

## Summary
Severity: Medium
Advisory: CVE-2019-13114
Aliases: PYSEC-2019-257
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13114
Type: osv

## Details
http.c in Exiv2 through 0.27.1 allows a malicious http server to cause a denial of service (crash due to a NULL pointer dereference) by returning a crafted response that lacks a space character.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FGBT5OD2TF4AIXJUC56WOUJRHAZLZ4DC/
- https://support.f5.com/csp/article/K45429077?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/4056-1/
- https://github.com/Exiv2/exiv2/issues/793
- https://github.com/Exiv2/exiv2/pull/815

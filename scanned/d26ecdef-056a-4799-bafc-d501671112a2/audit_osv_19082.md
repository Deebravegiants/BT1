# [H] CVE-2020-7044

## Summary
Severity: High
Advisory: CVE-2020-7044
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-16
Source: https://osv.dev/vulnerability/CVE-2020-7044
Type: osv

## Details
In Wireshark 3.2.x before 3.2.1, the WASSP dissector could crash. This was addressed in epan/dissectors/packet-wassp.c by using >= and <= to resolve off-by-one errors.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f90a3720b73ca140403315126e2a478c4f70ca03
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DZBICEY2HGSNQ3RPBLMDDYVAHGOGS4E2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JDVMBCADP73TBISYCS6ARKOSNNJOGXXZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XN2GMGLT5XND7U34WX3O23WKUZ7JHMVN/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://www.wireshark.org/security/wnpa-sec-2020-01.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16324
- https://www.oracle.com/security-alerts/cpuapr2020.html

# [M] CVE-2018-19130

## Summary
Severity: Medium
Advisory: CVE-2018-19130
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-09
Source: https://osv.dev/vulnerability/CVE-2018-19130
Type: osv

## Details
In Libav 12.3, there is an invalid memory access in vc1_decode_frame in libavcodec/vc1dec.c that allows attackers to cause a denial-of-service via a crafted aac file. NOTE: This may be a duplicate of CVE-2017-17127

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00003.html
- https://exchange.xforce.ibmcloud.com/vulnerabilities/152819
- https://bugzilla.libav.org/show_bug.cgi?id=1139

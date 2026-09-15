# [H] CVE-2017-11521

## Summary
Severity: High
Advisory: CVE-2017-11521
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-22
Source: https://osv.dev/vulnerability/CVE-2017-11521
Type: osv

## Details
The SdpContents::Session::Medium::parse function in resip/stack/SdpContents.cxx in reSIProcate 1.10.2 allows remote attackers to cause a denial of service (memory consumption) by triggering many media connections.

## References
- https://list.resiprocate.org/archive/resiprocate-users/msg02701.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00029.html
- https://github.com/resiprocate/resiprocate/pull/88

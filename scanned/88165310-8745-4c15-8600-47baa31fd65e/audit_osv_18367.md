# [H] CVE-2020-26575

## Summary
Severity: High
Advisory: CVE-2020-26575
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-2020-26575
Type: osv

## Details
In Wireshark through 3.2.7, the Facebook Zero Protocol (aka FBZERO) dissector could enter an infinite loop. This was addressed in epan/dissectors/packet-fbzero.c by correcting the implementation of offset advancement.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UHZSVK7PO2LTGFQXFHFXY6SOMSQ7UPRS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V2667E6WKVE56G66BVBVD7LJPIDOJ7K3/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://security.gentoo.org/glsa/202011-08
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.wireshark.org/security/wnpa-sec-2020-14.html
- https://gitlab.com/wireshark/wireshark/-/issues/16887
- https://gitlab.com/wireshark/wireshark/-/commit/3ff940652962c099b73ae3233322b8697b0d10ab
- https://gitlab.com/wireshark/wireshark/-/merge_requests/467
- https://gitlab.com/wireshark/wireshark/-/merge_requests/471
- https://gitlab.com/wireshark/wireshark/-/merge_requests/472
- https://gitlab.com/wireshark/wireshark/-/merge_requests/473

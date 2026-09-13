# [M] CVE-2020-27830

## Summary
Severity: Medium
Advisory: CVE-2020-27830
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2020-27830
Type: osv

## Details
A vulnerability was found in Linux Kernel where in the spk_ttyio_receive_buf2() function, it would dereference spk_ttyio_synth without checking whether it is NULL or not, and may lead to a NULL-ptr deref crash.

## References
- https://security.netapp.com/advisory/ntap-20210625-0004/
- https://www.debian.org/security/2021/dsa-4843
- http://www.openwall.com/lists/oss-security/2020/12/08/1
- http://www.openwall.com/lists/oss-security/2020/12/08/4
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1919900

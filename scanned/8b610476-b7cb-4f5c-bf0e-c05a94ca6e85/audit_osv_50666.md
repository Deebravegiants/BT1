# [H] CVE-2020-27672

## Summary
Severity: High
Advisory: CVE-2020-27672
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-22
Source: https://osv.dev/vulnerability/CVE-2020-27672
Type: osv

## Details
An issue was discovered in Xen through 4.14.x allowing x86 guest OS users to cause a host OS denial of service, achieve data corruption, or possibly gain privileges by exploiting a race condition that leads to a use-after-free involving 2MiB and 1GiB superpages.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XIK57QJOVOPWH6RFRNMGOBCROBCKMDG2/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00075.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00025.html
- http://www.openwall.com/lists/oss-security/2021/01/19/7
- https://security.gentoo.org/glsa/202011-06
- https://www.debian.org/security/2020/dsa-4804
- http://xenbits.xen.org/xsa/advisory-345.html
- https://xenbits.xen.org/xsa/advisory-345.html

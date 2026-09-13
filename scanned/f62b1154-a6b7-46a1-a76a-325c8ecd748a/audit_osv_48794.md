# [H] CVE-2018-14348

## Summary
Severity: High
Advisory: CVE-2018-14348
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-08-14
Source: https://osv.dev/vulnerability/CVE-2018-14348
Type: osv

## Details
libcgroup up to and including 0.41 creates /var/log/cgred with mode 0666 regardless of the configured umask, leading to disclosure of information.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-08/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3VH333EONOEEGKOLHHFXCJYHCYMHJ4KK/
- https://access.redhat.com/errata/RHSA-2019:2047
- https://lists.debian.org/debian-lts-announce/2018/08/msg00019.html
- https://bugzilla.suse.com/show_bug.cgi?id=1100365
- https://sourceforge.net/p/libcg/libcg/ci/0d88b73d189ea3440ccaab00418d6469f76fa590/

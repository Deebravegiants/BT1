# [H] CVE-2019-14378

## Summary
Severity: High
Advisory: CVE-2019-14378
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-29
Source: https://osv.dev/vulnerability/CVE-2019-14378
Type: osv

## Details
ip_reass in ip_input.c in libslirp 4.0.0 has a heap-based buffer overflow via a large packet because it mishandles a case involving the first fragment.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00034.html
- http://packetstormsecurity.com/files/154269/QEMU-Denial-Of-Service.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPLHB2AN663OXAWUQURF7J2X5LHD4VD3/
- https://news.ycombinator.com/item?id=20799010
- https://seclists.org/bugtraq/2019/Aug/41
- https://seclists.org/bugtraq/2019/Sep/3
- https://support.f5.com/csp/article/K25423748
- https://support.f5.com/csp/article/K25423748?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/4191-1/
- https://usn.ubuntu.com/4191-2/
- http://www.openwall.com/lists/oss-security/2019/08/01/2
- https://access.redhat.com/errata/RHSA-2019:3179
- https://access.redhat.com/errata/RHSA-2019:3403
- https://access.redhat.com/errata/RHSA-2019:3494
- https://access.redhat.com/errata/RHSA-2019:3742
- https://access.redhat.com/errata/RHSA-2019:3787
- https://access.redhat.com/errata/RHSA-2019:3968

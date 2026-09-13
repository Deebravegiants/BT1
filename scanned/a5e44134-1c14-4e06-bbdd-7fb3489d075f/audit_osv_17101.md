# [M] CVE-2020-12430

## Summary
Severity: Medium
Advisory: CVE-2020-12430
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/CVE-2020-12430
Type: osv

## Details
An issue was discovered in qemuDomainGetStatsIOThread in qemu/qemu_driver.c in libvirt 4.10.0 though 6.x before 6.1.0. A memory leak was found in the virDomainListGetStats libvirt API that is responsible for retrieving domain statistics when managing QEMU guests. This flaw allows unprivileged users with a read-only connection to cause a memory leak in the domstats command, resulting in a potential denial of service.

## References
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=9bf9e0ae6af38c806f4672ca7b12a6b38d5a9581
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D5GE6ISYUL3CIWO3FQRUGMKTKP2NYED2/
- https://usn.ubuntu.com/4371-1/
- https://security.netapp.com/advisory/ntap-20200518-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=1804548
- https://bugzilla.redhat.com/show_bug.cgi?id=1828190

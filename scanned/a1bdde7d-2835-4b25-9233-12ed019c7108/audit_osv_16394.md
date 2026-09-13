# [M] CVE-2019-6454

## Summary
Severity: Medium
Advisory: CVE-2019-6454
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-6454
Type: osv

## Details
An issue was discovered in sd-bus in systemd 239. bus_process_object() in libsystemd/sd-bus/bus-objects.c allocates a variable-length stack buffer for temporarily storing the object path of incoming D-Bus messages. An unprivileged local user can exploit this by sending a specially crafted message to PID1, causing the stack pointer to jump over the stack guard pages into an unmapped memory region and trigger a denial of service (systemd PID1 crash and kernel panic).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N67IOBOTDOMVNQJ5QRU2MXLEECXPGNVJ/
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00070.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00062.html
- http://www.openwall.com/lists/oss-security/2019/02/19/1
- http://www.securityfocus.com/bid/107081
- https://access.redhat.com/errata/RHSA-2019:0368
- https://access.redhat.com/errata/RHSA-2019:0990
- https://access.redhat.com/errata/RHSA-2019:1322
- https://access.redhat.com/errata/RHSA-2019:1502
- https://access.redhat.com/errata/RHSA-2019:2805
- https://lists.debian.org/debian-lts-announce/2019/02/msg00031.html
- https://security.netapp.com/advisory/ntap-20190327-0004/
- https://usn.ubuntu.com/3891-1/
- https://www.debian.org/security/2019/dsa-4393
- http://www.openwall.com/lists/oss-security/2019/02/18/3
- https://github.com/systemd/systemd/commits/master/src/libsystemd/sd-bus/bus-objects.c
- https://kc.mcafee.com/corporate/index?page=content&id=SB10278
- http://www.openwall.com/lists/oss-security/2021/07/20/2

# [C] CVE-2018-20815

## Summary
Severity: Critical
Advisory: CVE-2018-20815
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2018-20815
Type: osv

## Details
In QEMU 3.1.0, load_device_tree in device_tree.c calls the deprecated load_image function, which has a buffer overflow risk.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=da885fe1ee8b4589047484bd7fa05a4905b52b17
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BOE3PVFPMWMXV3DGP2R3XIHAF2ZQU3FS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVDHJB2QKXNDU7OFXIHIL5O5VN5QCSZL/
- https://seclists.org/bugtraq/2019/Aug/41
- https://access.redhat.com/errata/RHSA-2019:1667
- https://access.redhat.com/errata/RHSA-2019:1723
- https://access.redhat.com/errata/RHSA-2019:1743
- https://access.redhat.com/errata/RHSA-2019:1881
- https://access.redhat.com/errata/RHSA-2019:1968
- https://access.redhat.com/errata/RHSA-2019:2507
- https://access.redhat.com/errata/RHSA-2019:2553
- https://www.debian.org/security/2019/dsa-4506

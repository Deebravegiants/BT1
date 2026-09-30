# [M] CVE-2019-3882

## Summary
Severity: Medium
Advisory: CVE-2019-3882
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-3882
Type: osv

## Details
A flaw was found in the Linux kernel's vfio interface implementation that permits violation of the user's locked memory limit. If a device is bound to a vfio driver, such as vfio-pci, and the local attacker is administratively granted ownership of the device, it may cause a system memory exhaustion and thus a denial of service (DoS). Versions 3.10, 4.14 and 4.18 are vulnerable.

## References
- https://usn.ubuntu.com/3981-1/
- https://access.redhat.com/errata/RHSA-2019:3309
- https://lists.debian.org/debian-lts-announce/2019/05/msg00042.html
- https://seclists.org/bugtraq/2019/Aug/18
- https://security.netapp.com/advisory/ntap-20190517-0005/
- https://usn.ubuntu.com/3982-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00071.html
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:3517
- https://usn.ubuntu.com/3979-1/
- https://usn.ubuntu.com/3980-2/
- https://usn.ubuntu.com/3982-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00037.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://usn.ubuntu.com/3981-2/
- https://www.debian.org/security/2019/dsa-4497
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00043.html
- https://access.redhat.com/errata/RHSA-2019:2043
- https://usn.ubuntu.com/3980-1/

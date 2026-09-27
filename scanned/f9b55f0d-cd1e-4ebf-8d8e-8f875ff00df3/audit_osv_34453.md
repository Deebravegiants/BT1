# [H] Libblockdev: lpe from allow_active to root in libblockdev via udisks

## Summary
Severity: High
Advisory: CVE-2025-6019
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-6019
Type: osv

## Details
A Local Privilege Escalation (LPE) vulnerability was found in libblockdev. Generally, the "allow_active" setting in Polkit permits a physically present user to take certain actions based on the session type. Due to the way libblockdev interacts with the udisks daemon, an "allow_active" user on a system may be able escalate to full root privileges on the target host. Normally, udisks mounts user-provided filesystem images with security flags like nosuid and nodev to prevent privilege escalation.  However, a local attacker can create a specially crafted XFS image containing a SUID-root shell, then trick udisks into resizing it. This mounts their malicious filesystem with root privileges, allowing them to execute their SUID-root shell and gain complete control of the system.

## References
- http://www.openwall.com/lists/oss-security/2025/06/17/5
- http://www.openwall.com/lists/oss-security/2025/06/17/6
- http://www.openwall.com/lists/oss-security/2025/06/18/1
- https://access.redhat.com/downloads/content/package-browser/
- https://cdn2.qualys.com/2025/06/17/suse15-pam-udisks-lpe.txt
- https://github.com/storaged-project/libblockdev/
- https://lists.debian.org/debian-lts-announce/2025/06/msg00018.html
- https://news.ycombinator.com/item?id=44325861
- https://www.bleepingcomputer.com/news/linux/new-linux-udisks-flaw-lets-attackers-get-root-on-major-linux-distros/
- https://access.redhat.com/errata/RHSA-2025:10796
- https://access.redhat.com/errata/RHSA-2025:9320
- https://access.redhat.com/errata/RHSA-2025:9321
- https://access.redhat.com/errata/RHSA-2025:9322
- https://access.redhat.com/errata/RHSA-2025:9323
- https://access.redhat.com/errata/RHSA-2025:9324
- https://access.redhat.com/errata/RHSA-2025:9325
- https://access.redhat.com/errata/RHSA-2025:9326
- https://access.redhat.com/errata/RHSA-2025:9327
- https://access.redhat.com/errata/RHSA-2025:9328
- https://access.redhat.com/errata/RHSA-2025:9878

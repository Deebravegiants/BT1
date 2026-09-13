# [H] CVE-2017-1000256

## Summary
Severity: High
Advisory: CVE-2017-1000256
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-31
Source: https://osv.dev/vulnerability/CVE-2017-1000256
Type: osv

## Details
libvirt version 2.3.0 and later is vulnerable to a bad default configuration of "verify-peer=no" passed to QEMU by libvirt resulting in a failure to validate SSL/TLS certificates by default.

## References
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1556251.html
- http://www.debian.org/security/2017/dsa-4003
- https://access.redhat.com/security/cve/CVE-2017-1000256
- https://www.redhat.com/archives/libvirt-announce/2017-October/msg00001.html

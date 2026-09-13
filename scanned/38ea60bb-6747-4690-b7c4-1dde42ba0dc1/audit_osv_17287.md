# [H] CVE-2020-14339

## Summary
Severity: High
Advisory: CVE-2020-14339
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-14339
Type: osv

## Details
A flaw was found in libvirt, where it leaked a file descriptor for `/dev/mapper/control` into the QEMU process. This file descriptor allows for privileged operations to happen against the device-mapper on the host. This flaw allows a malicious guest user or process to perform operations outside of their standard permissions, potentially causing serious damage to the host operating system. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.gentoo.org/glsa/202101-22
- https://security.gentoo.org/glsa/202210-06
- https://bugzilla.redhat.com/show_bug.cgi?id=1860069

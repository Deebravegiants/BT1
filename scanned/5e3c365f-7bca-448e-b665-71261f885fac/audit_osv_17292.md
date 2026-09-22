# [M] CVE-2020-14355

## Summary
Severity: Medium
Advisory: CVE-2020-14355
CVSS: 6.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-10-07
Source: https://osv.dev/vulnerability/CVE-2020-14355
Type: osv

## Details
Multiple buffer overflow vulnerabilities were found in the QUIC image decoding process of the SPICE remote display system, before spice-0.14.2-1. Both the SPICE client (spice-gtk) and server are affected by these flaws. These flaws allow a malicious client or server to send specially crafted messages that, when processed by the QUIC image compression algorithm, result in a process crash or potential code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00002.html
- https://usn.ubuntu.com/4572-1/
- https://usn.ubuntu.com/4572-2/
- https://www.debian.org/security/2020/dsa-4771
- https://bugzilla.redhat.com/show_bug.cgi?id=1868435
- https://www.openwall.com/lists/oss-security/2020/10/06/10

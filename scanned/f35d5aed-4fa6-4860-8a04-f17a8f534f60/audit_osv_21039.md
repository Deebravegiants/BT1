# [H] CVE-2021-3999

## Summary
Severity: High
Advisory: CVE-2021-3999
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-3999
Type: osv

## Details
A flaw was found in glibc. An off-by-one buffer overflow and underflow in getcwd() may lead to memory corruption when the size of the buffer is exactly 1. A local attacker who can control the input buffer and size passed to getcwd() in a setuid program could use this flaw to potentially execute arbitrary code and escalate their privileges on the system.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=23e0e8f5f1fb5ed150253d986ecccdc90c2dcd5e
- https://access.redhat.com/security/cve/CVE-2021-3999
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security-tracker.debian.org/tracker/CVE-2021-3999
- https://security.netapp.com/advisory/ntap-20221104-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2024637
- https://sourceware.org/bugzilla/show_bug.cgi?id=28769
- https://www.openwall.com/lists/oss-security/2022/01/24/4

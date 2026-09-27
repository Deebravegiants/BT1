# [M] CVE-2020-14310

## Summary
Severity: Medium
Advisory: CVE-2020-14310
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-07-31
Source: https://osv.dev/vulnerability/CVE-2020-14310
Type: osv

## Details
There is an issue on grub2 before version 2.06 at function read_section_as_string(). It expects a font name to be at max UINT32_MAX - 1 length in bytes but it doesn't verify it before proceed with buffer allocation to read the value from the font value. An attacker may leverage that by crafting a malicious font file which has a name with UINT32_MAX, leading to read_section_as_string() to an arithmetic overflow, zero-sized allocation and further heap-based buffer overflow.

## References
- https://security.gentoo.org/glsa/202104-05
- https://usn.ubuntu.com/4432-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14310

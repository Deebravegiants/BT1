# [H] CVE-2020-14381

## Summary
Severity: High
Advisory: CVE-2020-14381
Aliases: A-175193031, ASB-A-175193031
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-14381
Type: osv

## Details
A flaw was found in the Linux kernel’s futex implementation. This flaw allows a local attacker to corrupt system memory or escalate their privileges when creating a futex on a filesystem that is about to be unmounted. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1874311
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8019ad13ef7f64be44d4f892af9c840179009254

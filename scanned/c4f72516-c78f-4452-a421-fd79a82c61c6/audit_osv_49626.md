# [H] CVE-2019-14855

## Summary
Severity: High
Advisory: CVE-2019-14855
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2019-14855
Type: osv

## Details
A flaw was found in the way certificate signatures could be forged using collisions found in the SHA-1 algorithm. An attacker could use this weakness to create forged certificate signatures. This issue affects GnuPG versions before 2.2.18.

## References
- https://dev.gnupg.org/T4755
- https://lists.gnupg.org/pipermail/gnupg-announce/2019q4/000442.html
- https://usn.ubuntu.com/4516-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14855
- https://rwc.iacr.org/2020/slides/Leurent.pdf

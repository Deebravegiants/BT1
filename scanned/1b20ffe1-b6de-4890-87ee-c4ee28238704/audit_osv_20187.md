# [C] CVE-2021-32055

## Summary
Severity: Critical
Advisory: CVE-2021-32055
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-05-05
Source: https://osv.dev/vulnerability/CVE-2021-32055
Type: osv

## Details
Mutt 1.11.0 through 2.0.x before 2.0.7 (and NeoMutt 2019-10-25 through 2021-05-04) has a $imap_qresync issue in which imap/util.c has an out-of-bounds read in situations where an IMAP sequence set ends with a comma. NOTE: the $imap_qresync setting for QRESYNC is not enabled by default.

## References
- http://lists.mutt.org/pipermail/mutt-announce/Week-of-Mon-20210503/000036.html
- https://security.gentoo.org/glsa/202105-05
- https://github.com/neomutt/neomutt/commit/fa1db5785e5cfd9d3cd27b7571b9fe268d2ec2dc
- https://gitlab.com/muttmua/mutt/-/commit/7c4779ac24d2fb68a2a47b58c7904118f40965d5

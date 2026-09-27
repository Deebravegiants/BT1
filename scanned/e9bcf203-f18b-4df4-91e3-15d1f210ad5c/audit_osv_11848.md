# [H] CVE-2018-0496

## Summary
Severity: High
Advisory: CVE-2018-0496
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-0496
Type: osv

## Details
Directory traversal issues in the D-Mod extractor in DFArc and DFArc2 (as well as in RTsoft's Dink Smallwood HD / ProtonSDK version) before 3.14 allow an attacker to overwrite arbitrary files on the user's system.

## References
- https://lists.debian.org/debian-lts-announce/2019/02/msg00033.html
- https://savannah.gnu.org/forum/forum.php?forum_id=9169
- https://git.savannah.gnu.org/cgit/freedink/dfarc.git/commit/?id=40cc957f52e772f45125126439ba9333cf2d2998

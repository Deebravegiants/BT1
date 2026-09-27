# [H] CVE-2023-27635

## Summary
Severity: High
Advisory: CVE-2023-27635
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-05
Source: https://osv.dev/vulnerability/CVE-2023-27635
Type: osv

## Details
debmany in debian-goodies 0.88.1 allows attackers to execute arbitrary shell commands (because of an eval call) via a crafted .deb file. (The path is shown to the user before execution.)

## References
- https://bugs.debian.org/1031267

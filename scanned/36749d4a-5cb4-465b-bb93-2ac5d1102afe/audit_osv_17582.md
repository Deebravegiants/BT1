# [H] CVE-2020-17354

## Summary
Severity: High
Advisory: CVE-2020-17354
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2020-17354
Type: osv

## Details
LilyPond before 2.24 allows attackers to bypass the -dsafe protection mechanism via output-def-lookup or output-def-scope, as demonstrated by dangerous Scheme code in a .ly file that causes arbitrary code execution during conversion to a different file format. NOTE: in 2.24 and later versions, safe mode is removed, and the product no longer tries to block code execution when external files are used.

## References
- https://lilypond.org/download.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K43PF6VGFJNNGAPY57BW3VMEFFOSMRLF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ST5BLLQ4GDME3SN7UE5OMNE5GZE66X4Y/
- http://lilypond.org/doc/v2.18/Documentation/usage/command_002dline-usage
- https://tracker.debian.org/news/1249694/accepted-lilypond-2221-1-source-into-unstable/
- https://www.mediawiki.org/wiki/Extension:Score/2021_security_advisory
- https://gitlab.com/lilypond/lilypond/-/merge_requests/1522
- https://phabricator.wikimedia.org/T259210

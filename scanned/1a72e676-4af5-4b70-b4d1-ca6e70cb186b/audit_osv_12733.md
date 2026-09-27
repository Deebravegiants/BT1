# [H] CVE-2018-14553

## Summary
Severity: High
Advisory: CVE-2018-14553
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/CVE-2018-14553
Type: osv

## Details
gdImageClone in gd.c in libgd 2.1.0-rc2 through 2.2.5 has a NULL pointer dereference allowing attackers to crash an application via a specific function call sequence. Only affects PHP when linked with an external libgd (not bundled).

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3CZ2QADQTKRHTGB2AHD7J4QQNDLBEMM6/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00020.html
- https://github.com/libgd/libgd/pull/580
- https://lists.debian.org/debian-lts-announce/2020/02/msg00014.html
- https://usn.ubuntu.com/4316-1/
- https://usn.ubuntu.com/4316-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=1599032
- https://github.com/libgd/libgd/commit/a93eac0e843148dc2d631c3ba80af17e9c8c860f

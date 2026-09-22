# [M] CVE-2015-4645

## Summary
Severity: Medium
Advisory: CVE-2015-4645
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2015-4645
Type: osv

## Details
Integer overflow in the read_fragment_table_4 function in unsquash-4.c in Squashfs and sasquatch allows remote attackers to cause a denial of service (application crash) via a crafted input, which triggers a stack-based buffer overflow.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/162171.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-July/162226.html
- http://www.securityfocus.com/bid/75272
- https://bugzilla.redhat.com/show_bug.cgi?id=1234886
- https://github.com/devttys0/sasquatch/pull/5
- https://github.com/plougher/squashfs-tools/commit/f95864afe8833fe3ad782d714b41378e860977b1
- https://security.gentoo.org/glsa/201701-73
- https://bugzilla.redhat.com/show_bug.cgi?id=1234886

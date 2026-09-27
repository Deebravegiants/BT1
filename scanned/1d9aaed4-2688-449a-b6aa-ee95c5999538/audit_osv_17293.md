# [H] CVE-2020-14363

## Summary
Severity: High
Advisory: CVE-2020-14363
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2020-14363
Type: osv

## Details
An integer overflow vulnerability leading to a double-free was found in libX11. This flaw allows a local privileged attacker to cause an application compiled with libX11 to crash, or in some cases, result in arbitrary code execution. The highest threat from this flaw is to confidentiality, integrity as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7AVXCQOSCAPKYYHFIJAZ6E2C7LJBTLXF/
- https://github.com/Ruia-ruia/Exploits/blob/master/DFX11details.txt
- https://lists.x.org/archives/xorg-announce/2020-August/003056.html
- https://usn.ubuntu.com/4487-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14363
- https://github.com/Ruia-ruia/Exploits/blob/master/x11doublefree.sh

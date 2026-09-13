# [H] An integer overflow vulnerability leading to a double-free was found in libX11

## Summary
Severity: High
Advisory: JLSEC-2026-470
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-470
Type: osv

## Affected
- Julia: `Xorg_libX11_jll` — affected >=0 <1.8.6+0

## Details
An integer overflow vulnerability leading to a double-free was found in libX11. This flaw allows a local privileged attacker to cause an application compiled with libX11 to crash, or in some cases, result in arbitrary code execution. The highest threat from this flaw is to confidentiality, integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14363
- https://github.com/Ruia-ruia/Exploits/blob/master/DFX11details.txt
- https://github.com/Ruia-ruia/Exploits/blob/master/x11doublefree.sh
- https://github.com/advisories/GHSA-qmwg-hw9q-xg39
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7AVXCQOSCAPKYYHFIJAZ6E2C7LJBTLXF/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7AVXCQOSCAPKYYHFIJAZ6E2C7LJBTLXF/
- https://lists.x.org/archives/xorg-announce/2020-August/003056.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-14363
- https://usn.ubuntu.com/4487-2/

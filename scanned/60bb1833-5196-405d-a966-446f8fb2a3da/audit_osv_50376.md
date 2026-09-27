# [H] CVE-2020-14346

## Summary
Severity: High
Advisory: CVE-2020-14346
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-14346
Type: osv

## Details
A flaw was found in xorg-x11-server before 1.20.9. An integer underflow in the X input extension protocol decoding in the X server may lead to arbitrary access of memory contents. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://www.zerodayinitiative.com/advisories/ZDI-20-1417/
- https://security.gentoo.org/glsa/202012-01
- https://usn.ubuntu.com/4488-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=1862246
- https://lists.x.org/archives/xorg-announce/2020-August/003058.html

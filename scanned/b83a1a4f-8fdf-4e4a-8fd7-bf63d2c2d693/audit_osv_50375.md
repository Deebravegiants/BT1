# [H] CVE-2020-14345

## Summary
Severity: High
Advisory: CVE-2020-14345
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-14345
Type: osv

## Details
A flaw was found in X.Org Server before xorg-x11-server 1.20.9. An Out-Of-Bounds access in XkbSetNames function may lead to a privilege escalation vulnerability. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://usn.ubuntu.com/4488-2/
- https://usn.ubuntu.com/4490-1/
- https://www.zerodayinitiative.com/advisories/ZDI-20-1416/
- http://www.openwall.com/lists/oss-security/2021/01/15/1
- https://lists.x.org/archives/xorg-announce/2020-August/003058.html
- https://security.gentoo.org/glsa/202012-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1862241

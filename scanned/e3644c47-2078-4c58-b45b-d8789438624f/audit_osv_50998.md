# [C] CVE-2020-6831

## Summary
Severity: Critical
Advisory: CVE-2020-6831
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-26
Source: https://osv.dev/vulnerability/CVE-2020-6831
Type: osv

## Details
A buffer overflow could occur when parsing and validating SCTP chunks in WebRTC. This could have led to memory corruption and a potentially exploitable crash. This vulnerability affects Firefox ESR < 68.8, Firefox < 76, and Thunderbird < 68.8.0.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-16/
- https://www.mozilla.org/security/advisories/mfsa2020-17/
- http://packetstormsecurity.com/files/158480/usrsctp-Stack-Buffer-Overflow.html
- https://usn.ubuntu.com/4373-1/
- https://www.mozilla.org/security/advisories/mfsa2020-18/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00000.html
- https://security.gentoo.org/glsa/202005-04
- https://www.debian.org/security/2020/dsa-4714
- https://bugzilla.mozilla.org/show_bug.cgi?id=1632241
- https://security.gentoo.org/glsa/202005-03

# [C] CVE-2017-7467

## Summary
Severity: Critical
Advisory: CVE-2017-7467
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-11
Source: https://osv.dev/vulnerability/CVE-2017-7467
Type: osv

## Details
A buffer overflow flaw was found in the way minicom before version 2.7.1 handled VT100 escape sequences. A malicious terminal device could potentially use this flaw to crash minicom, or execute arbitrary code in the context of the minicom process.

## References
- https://security.gentoo.org/glsa/201706-13
- http://www.securityfocus.com/bid/97966
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7467
- http://www.openwall.com/lists/oss-security/2017/04/18/5

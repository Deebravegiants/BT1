# [H] CVE-2016-6321

## Summary
Severity: High
Advisory: CVE-2016-6321
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-6321
Type: osv

## Details
Directory traversal vulnerability in the safer_name_suffix function in GNU tar 1.14 through 1.29 might allow remote attackers to bypass an intended protection mechanism and write to arbitrary files via vectors related to improper sanitization of the file_name parameter, aka POINTYFEATHER.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.gnu.org/archive/html/bug-tar/2016-10/msg00016.html
- http://seclists.org/fulldisclosure/2016/Oct/96
- http://www.debian.org/security/2016/dsa-3702
- http://www.securityfocus.com/bid/93937
- http://www.ubuntu.com/usn/USN-3132-1
- https://security.gentoo.org/glsa/201611-19
- https://sintonen.fi/advisories/tar-extract-pathname-bypass.proper.txt
- http://git.savannah.gnu.org/cgit/tar.git/commit/?id=7340f67b9860ea0531c1450e5aa261c50f67165d
- http://seclists.org/fulldisclosure/2016/Oct/102
- http://packetstormsecurity.com/files/139370/GNU-tar-1.29-Extract-Pathname-Bypass.html

# [C] CVE-2016-2851

## Summary
Severity: Critical
Advisory: CVE-2016-2851
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2016-2851
Type: osv

## Details
Integer overflow in proto.c in libotr before 4.1.1 on 64-bit platforms allows remote attackers to cause a denial of service (memory corruption and application crash) or execute arbitrary code via a series of large OTR messages, which triggers a heap-based buffer overflow.

## References
- https://www.exploit-db.com/exploits/39550/
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00030.html
- http://www.debian.org/security/2016/dsa-3512
- http://www.securityfocus.com/archive/1/537745/100/0/threaded
- https://security.gentoo.org/glsa/201701-10
- http://www.securityfocus.com/bid/84285
- http://www.ubuntu.com/usn/USN-2926-1
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00021.html
- https://www.x41-dsec.de/lab/advisories/x41-2016-001-libotr/
- http://seclists.org/fulldisclosure/2016/Mar/21
- https://lists.cypherpunks.ca/pipermail/otr-users/2016-March/002581.html

# [H] CVE-2018-18820

## Summary
Severity: High
Advisory: CVE-2018-18820
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-05
Source: https://osv.dev/vulnerability/CVE-2018-18820
Type: osv

## Details
A buffer overflow was discovered in the URL-authentication backend of the Icecast before 2.4.4. If the backend is enabled, then any malicious HTTP client can send a request for that specific resource including a crafted header, leading to denial of service and potentially remote code execution.

## References
- http://www.securitytracker.com/id/1042019
- https://lists.debian.org/debian-lts-announce/2018/11/msg00033.html
- https://security.gentoo.org/glsa/201811-09
- https://www.debian.org/security/2018/dsa-4333
- http://www.openwall.com/lists/oss-security/2018/11/01/3

# [H] CVE-2021-20275

## Summary
Severity: High
Advisory: CVE-2021-20275
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-20275
Type: osv

## Details
A flaw was found in privoxy before 3.0.32. A invalid read of size two may occur in chunked_body_is_complete() leading to denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2021/03/msg00009.html
- https://security.gentoo.org/glsa/202107-16
- https://www.privoxy.org/announce.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=1936666

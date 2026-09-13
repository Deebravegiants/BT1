# [C] CVE-2021-33913

## Summary
Severity: Critical
Advisory: CVE-2021-33913
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-19
Source: https://osv.dev/vulnerability/CVE-2021-33913
Type: osv

## Details
libspf2 before 1.2.11 has a heap-based buffer overflow that might allow remote attackers to execute arbitrary code (via an unauthenticated e-mail message from anywhere on the Internet) with a crafted SPF DNS record, because of SPF_record_expand_data in spf_expand.c. The amount of overflowed data depends on the relationship between the length of an entire domain name and the length of its leftmost label. The vulnerable code may be part of the supply chain of a site's e-mail infrastructure (e.g., with additional configuration, Exim can use libspf2; the Postfix web site links to unofficial patches for use of libspf2 with Postfix; older versions of spfquery relied on libspf2) but most often is not.

## References
- https://github.com/shevek/libspf2/tree/8131fe140704eaae695e76b5cd09e39bd1dd220b
- https://lists.debian.org/debian-lts-announce/2022/01/msg00015.html
- https://security.gentoo.org/glsa/202401-22
- https://nathanielbennett.com/blog/libspf2-cve-jan-2022-disclosure

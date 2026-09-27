# [C] ALPINE-CVE-2021-33913

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-33913
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-33913
Type: osv

## Affected
- Alpine:v3.14: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.15: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.16: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.17: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.18: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.19: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.20: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.21: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.22: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.23: `libspf2` — affected >=0 <1.2.11-r0
- Alpine:v3.24: `libspf2` — affected >=0 <1.2.11-r0

## Details
libspf2 before 1.2.11 has a heap-based buffer overflow that might allow remote attackers to execute arbitrary code (via an unauthenticated e-mail message from anywhere on the Internet) with a crafted SPF DNS record, because of SPF_record_expand_data in spf_expand.c. The amount of overflowed data depends on the relationship between the length of an entire domain name and the length of its leftmost label. The vulnerable code may be part of the supply chain of a site's e-mail infrastructure (e.g., with additional configuration, Exim can use libspf2; the Postfix web site links to unofficial patches for use of libspf2 with Postfix; older versions of spfquery relied on libspf2) but most often is not.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-33913

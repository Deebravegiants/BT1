# [H] ALPINE-CVE-2024-56406

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-56406
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-56406
Type: osv

## Affected
- Alpine:v3.18: `perl` — affected >=5.33.1 <5.36.2-r1
- Alpine:v3.19: `perl` — affected >=5.33.1 <5.38.3-r1
- Alpine:v3.20: `perl` — affected >=5.33.1 <5.38.3-r1
- Alpine:v3.21: `perl` — affected >=5.33.1 <5.40.1-r1
- Alpine:v3.22: `perl` — affected >=5.33.1 <5.40.1-r1
- Alpine:v3.23: `perl` — affected >=5.33.1 <5.40.1-r1
- Alpine:v3.24: `perl` — affected >=5.33.1 <5.40.1-r1

## Details
A heap buffer overflow vulnerability was discovered in Perl. 

Release branches 5.34, 5.36, 5.38 and 5.40 are affected, including development versions from 5.33.1 through 5.41.10.

When there are non-ASCII bytes in the left-hand-side of the `tr` operator, `S_do_trans_invmap` can overflow the destination pointer `d`.

   $ perl -e '$_ = "\x{FF}" x 1000000; tr/\xFF/\x{100}/;' 
   Segmentation fault (core dumped)

It is believed that this vulnerability can enable Denial of Service and possibly Code Execution attacks on platforms that lack sufficient defenses.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-56406

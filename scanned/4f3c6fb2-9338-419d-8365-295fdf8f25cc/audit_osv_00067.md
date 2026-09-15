# [C] ALPINE-CVE-2016-1283

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-1283
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-1283
Type: osv

## Affected
- Alpine:v3.4: `pcre` — affected >=0 <8.38-r1
- Alpine:v3.5: `php5` — affected >=0 <5.6.32-r0

## Details
The pcre_compile2 function in pcre_compile.c in PCRE 8.38 mishandles the /((?:F?+(?:^(?(R)a+\"){99}-))(?J)(?'R'(?'R'<((?'RR'(?'R'\){97)?J)?J)(?'R'(?'R'\){99|(:(?|(?'R')(\k'R')|((?'R')))H'R'R)(H'R))))))/ pattern and related patterns with named subgroups, which allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via a crafted regular expression, as demonstrated by a JavaScript RegExp object encountered by Konqueror.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-1283

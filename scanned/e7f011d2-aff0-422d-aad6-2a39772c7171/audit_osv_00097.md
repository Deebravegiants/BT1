# [C] ALPINE-CVE-2016-3191

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-3191
Ecosystem: Alpine:v3.4
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-03-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-3191
Type: osv

## Affected
- Alpine:v3.4: `pcre` — affected >=0 <8.38-r1

## Details
The compile_branch function in pcre_compile.c in PCRE 8.x before 8.39 and pcre2_compile.c in PCRE2 before 10.22 mishandles patterns containing an (*ACCEPT) substring in conjunction with nested parentheses, which allows remote attackers to execute arbitrary code or cause a denial of service (stack-based buffer overflow) via a crafted regular expression, as demonstrated by a JavaScript RegExp object encountered by Konqueror, aka ZDI-CAN-3542.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-3191

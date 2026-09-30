# [H] ALPINE-CVE-2018-12116

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12116
Ecosystem: Alpine:v3.8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12116
Type: osv

## Affected
- Alpine:v3.8: `nodejs` — affected >=0 <8.14.0-r0

## Details
Node.js: All versions prior to Node.js 6.15.0 and 8.14.0: HTTP request splitting: If Node.js can be convinced to use unsanitized user-provided Unicode data for the `path` option of an HTTP request, then data can be provided which will trigger a second, unexpected, and user-defined HTTP request to made to the same server.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12116

# [H] ALPINE-CVE-2024-49767

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-49767
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-49767
Type: osv

## Affected
- Alpine:v3.23: `py3-werkzeug` — affected >=0 <3.0.6-r0
- Alpine:v3.24: `py3-werkzeug` — affected >=0 <3.0.6-r0

## Details
Werkzeug is a Web Server Gateway Interface web application library. Applications using `werkzeug.formparser.MultiPartParser` corresponding to a version of Werkzeug prior to 3.0.6 to parse `multipart/form-data` requests (e.g. all flask applications) are vulnerable to a relatively simple but effective resource exhaustion (denial of service) attack. A specifically crafted form submission request can cause the parser to allocate and block 3 to 8 times the upload size in main memory. There is no upper limit; a single upload at 1 Gbit/s can exhaust 32 GB of RAM in less than 60 seconds. Werkzeug version 3.0.6 fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-49767

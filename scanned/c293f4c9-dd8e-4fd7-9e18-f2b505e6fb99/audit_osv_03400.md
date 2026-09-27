# [H] ALPINE-CVE-2025-9086

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-9086
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-9086
Type: osv

## Affected
- Alpine:v3.19: `curl` — affected >=8.13.0 <8.14.1-r2
- Alpine:v3.20: `curl` — affected >=8.13.0 <8.14.1-r2
- Alpine:v3.21: `curl` — affected >=8.13.0 <8.14.1-r2
- Alpine:v3.22: `curl` — affected >=8.13.0 <8.14.1-r2
- Alpine:v3.23: `curl` — affected >=8.13.0 <8.16.0-r0
- Alpine:v3.24: `curl` — affected >=8.13.0 <8.16.0-r0

## Details
1. A cookie is set using the `secure` keyword for `https://target` 
 2. curl is redirected to or otherwise made to speak with `http://target` (same 
   hostname, but using clear text HTTP) using the same cookie set 
 3. The same cookie name is set - but with just a slash as path (`path=\"/\",`).
   Since this site is not secure, the cookie *should* just be ignored.
4. A bug in the path comparison logic makes curl read outside a heap buffer
   boundary

The bug either causes a crash or it potentially makes the comparison come to
the wrong conclusion and lets the clear-text site override the contents of the
secure cookie, contrary to expectations and depending on the memory contents
immediately following the single-byte allocation that holds the path.

The presumed and correct behavior would be to plainly ignore the second set of
the cookie since it was already set as secure on a secure host so overriding
it on an insecure host should not be okay.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-9086

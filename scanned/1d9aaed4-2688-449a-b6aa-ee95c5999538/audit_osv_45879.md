# [H] 1

## Summary
Severity: High
Advisory: JLSEC-2026-435
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-435
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.13.0+0 <8.16.0+0
- Julia: `LibCURL_jll` — affected >=8.13.0+0 <8.16.0+0

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
- http://www.openwall.com/lists/oss-security/2025/09/10/1
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://curl.se/docs/CVE-2025-9086.html
- https://curl.se/docs/CVE-2025-9086.json
- https://github.com/advisories/GHSA-v676-f8gm-92r9
- https://hackerone.com/reports/3294999
- https://lists.debian.org/debian-lts-announce/2026/01/msg00002.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-9086

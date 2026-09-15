# [H] ALPINE-CVE-2026-34580

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34580
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34580
Type: osv

## Affected
- Alpine:v3.24: `botan3` — affected >=0 <3.11.1-r0

## Details
Botan is a C++ cryptography library. In 3.11.0, the function Certificate_Store::certificate_known had a misleading name; it would return true if any certificate in the store had a DN (and subject key identifier, if set) matching that of the argument. It did not check that the cert it found and the cert it was passed were actually the same certificate. In 3.11.0 an extension of path validation logic was made which assumed that certificate_known only returned true if the certificates were in fact identical. The impact is that if an end entity certificate is presented, and its DN (and subject key identifier, if set) match that of any trusted root, the end entity certificate is accepted immediately as if it itself were a trusted root. , This vulnerability is fixed in 3.11.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34580

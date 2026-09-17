# [M] Mojolicious::Sessions::Storable versions through 0.05 for Perl generate session ids insecurely

## Summary
Severity: Medium
Advisory: CVE-2026-9692
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-9692
Type: osv

## Details
Mojolicious::Sessions::Storable versions through 0.05 for Perl generate session ids insecurely.

The default session id generator returns a SHA-1 hash seeded with the built-in rand function, the epoch time, the heap address of an anonymous hash, and the PID.

These are predictable or low-entropy sources that are unsuitable for security purposes.

## References
- https://cpan.org/modules
- https://metacpan.org/release/HAYAJO/Mojolicious-Plugin-SessionStore-0.05/source/lib/Mojolicious/Sessions/Storable.pm#L11-15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9692.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9692
- https://www.cve.org/CVERecord?id=CVE-2025-40923
- https://security.metacpan.org/patches/M/Mojolicious-Plugin-SessionStore/0.05/CVE-2026-9692-r1.patch
- https://github.com/hayajo/Mojolicious-Plugin-SessionStore
- https://security.metacpan.org/docs/guides/random-data-for-security.html

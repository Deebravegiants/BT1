# [C] Mojolicious versions from 4.59 before 9.48 for Perl expose a stable representation of the session CSRF token to a BREACH compression oracle

## Summary
Severity: Critical
Advisory: CVE-2026-15747
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-15747
Type: osv

## Details
Mojolicious versions from 4.59 before 9.48 for Perl expose a stable representation of the session CSRF token to a BREACH compression oracle.

_csrf_token generates and caches one token per session and returns the same value on every call, and _csrf_field places that value in a hidden `csrf_token` input. When a response carrying the token also echoes attacker-controlled input and is gzip-compressed, the chosen values and the resulting compressed lengths form a BREACH oracle.

An attacker able to query it can recover the token and pass csrf_protect validation.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/16
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15747.json
- https://metacpan.org/release/SRI/Mojolicious-9.48/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-15747
- https://github.com/mojolicious/mojo/commit/01921fbbbbeca2d1397e082d4a647f9b84c24e27.patch
- https://github.com/mojolicious/mojo

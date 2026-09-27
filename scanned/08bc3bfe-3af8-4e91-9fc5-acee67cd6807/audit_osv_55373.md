# [C] CVE-2025-40931

## Summary
Severity: Critical
Advisory: CVE-2025-40931
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2025-40931
Type: osv

## Details
Apache::Session::Generate::MD5 versions through 1.94 for Perl create insecure session id.

Apache::Session::Generate::MD5 generates session ids insecurely. The default session id generator returns a MD5 hash seeded with the built-in rand() function, the epoch time, and the PID. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage. Predicable session ids could allow an attacker to gain access to systems.

## References
- https://metacpan.org/dist/Apache-Session/source/lib/Apache/Session/Generate/MD5.pm#L27
- https://rt.cpan.org/Ticket/Display.html?id=173631
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- http://www.openwall.com/lists/oss-security/2026/03/05/3
- https://github.com/chorny/Apache-Session/issues/4

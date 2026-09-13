# [M] HTTP::Session2 versions before 1.12 for Perl may generate weak session ids using the rand() function

## Summary
Severity: Medium
Advisory: CVE-2026-3255
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-3255
Type: osv

## Details
HTTP::Session2 versions before 1.12 for Perl for Perl may generate weak session ids using the rand() function.

The HTTP::Session2 session id generator returns a SHA-1 hash seeded with the built-in rand function, the epoch time, and the PID. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand() function is unsuitable for cryptographic usage.

HTTP::Session2 after version 1.02 will attempt to use the /dev/urandom device to generate a session id, but if the device is unavailable (for example, under Windows), then it will revert to the insecure method described above.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/12
- https://cpan.org/modules
- https://metacpan.org/release/TOKUHIROM/HTTP-Session2-1.01/source/lib/HTTP/Session2/ServerStore.pm#L68
- https://metacpan.org/release/TOKUHIROM/HTTP-Session2-1.11/source/lib/HTTP/Session2/Random.pm#L35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3255.json
- https://metacpan.org/release/TOKUHIROM/HTTP-Session2-1.12/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-3255
- https://github.com/tokuhirom/HTTP-Session2/commit/9cfde4d7e0965172aef5dcfa3b03bb48df93e636.patch
- https://github.com/tokuhirom/HTTP-Session2

# [M] Ado::Sessions versions through 0.935 for Perl generates insecure session ids

## Summary
Severity: Medium
Advisory: CVE-2026-5083
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-5083
Type: osv

## Details
Ado::Sessions versions through 0.935 for Perl generates insecure session ids.

The session id is generated from a SHA-1 hash seeded with the built-in rand function, the epoch time, and the PID. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

Predicable session ids could allow an attacker to gain access to systems.

Note that Ado is no longer maintained, and has been removed from the CPAN index. It is still available on BackPAN.

## References
- http://www.openwall.com/lists/oss-security/2026/04/08/7
- https://backpan.perl.org/authors/id/B/BE/BEROV/Ado-0.935.tar.gz
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5083.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5083
- https://github.com/kberov/Ado/issues/112
- https://github.com/kberov/Ado
- https://security.metacpan.org/docs/guides/random-data-for-security.html

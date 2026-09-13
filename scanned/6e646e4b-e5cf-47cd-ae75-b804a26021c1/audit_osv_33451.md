# [H] Plack-Middleware-Session before version 0.35 for Perl generates session ids insecurely

## Summary
Severity: High
Advisory: CVE-2025-40923
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-40923
Type: osv

## Details
Plack-Middleware-Session before version 0.35 for Perl generates session ids insecurely.

The default session id generator returns a SHA-1 hash seeded with the built-in rand function, the epoch time, and the PID. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

Predicable session ids could allow an attacker to gain access to systems.

## References
- http://www.openwall.com/lists/oss-security/2025/07/16/4
- https://cpan.org/modules
- https://metacpan.org/release/MIYAGAWA/Plack-Middleware-Session-0.34/source/lib/Plack/Session/State.pm#L22
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40923.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40923
- https://github.com/plack/Plack-Middleware-Session/commit/1fbfbb355e34e7f4b3906f66cf958cedadd2b9be.patch
- https://github.com/plack/Plack-Middleware-Session/pull/52
- https://github.com/plack/Plack-Middleware-Session

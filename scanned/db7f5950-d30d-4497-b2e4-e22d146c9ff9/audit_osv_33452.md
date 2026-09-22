# [M] Catalyst::Plugin::Session before version 0.44 for Perl generates session ids insecurely

## Summary
Severity: Medium
Advisory: CVE-2025-40924
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-40924
Type: osv

## Details
Catalyst::Plugin::Session before version 0.44 for Perl generates session ids insecurely.

The session id is generated from a (usually SHA-1) hash of a simple counter, the epoch time, the built-in rand function, the PID and the current Catalyst context. This information is of low entropy. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

Predicable session ids could allow an attacker to gain access to systems.

## References
- https://cpan.org/modules
- https://metacpan.org/release/HAARG/Catalyst-Plugin-Session-0.43/source/lib/Catalyst/Plugin/Session.pm#L632
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40924.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40924
- https://github.com/perl-catalyst/Catalyst-Plugin-Session/pull/5
- https://github.com/perl-catalyst/Catalyst-Plugin-Session/commit/c0e2b4ab1e42ebce1008286db8c571b6ee98c22c.patch
- https://github.com/perl-catalyst/Catalyst-Plugin-Session

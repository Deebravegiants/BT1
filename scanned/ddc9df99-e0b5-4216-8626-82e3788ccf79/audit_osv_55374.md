# [H] CVE-2025-40932

## Summary
Severity: High
Advisory: CVE-2025-40932
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2025-40932
Type: osv

## Details
Apache::SessionX versions through 2.01 for Perl create insecure session id.

Apache::SessionX generates session ids insecurely. The default session id generator in Apache::SessionX::Generate::MD5 returns a MD5 hash seeded with the built-in rand() function, the epoch time, and the PID. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage. Predicable session ids could allow an attacker to gain access to systems.

## References
- https://metacpan.org/release/GRICHTER/Apache-SessionX-2.01/source/SessionX/Generate/MD5.pm#L29

# [C] Starch versions 0.14 and earlier generate session ids insecurely

## Summary
Severity: Critical
Advisory: CVE-2025-40925
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-20
Source: https://osv.dev/vulnerability/CVE-2025-40925
Type: osv

## Details
Starch versions 0.14 and earlier generate session ids insecurely.

The default session id generator returns a SHA-1 hash seeded with a counter, the epoch time, the built-in rand function, the PID, and internal Perl reference addresses. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

Predicable session ids could allow an attacker to gain access to systems.

## References
- https://cpan.org/modules
- https://metacpan.org/dist/Starch/source/lib/Starch/Manager.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40925.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40925
- https://github.com/bluefeet/Starch/commit/5573449e64e0660f7ee209d1eab5881d4ccbee3b.patch
- https://github.com/bluefeet/Starch/pull/5
- https://github.com/bluefeet/Starch

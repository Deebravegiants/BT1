# [M] A malicious TLS1.2 server can force a TLS1.3 client with downgrade capability to use a ciphersuite...

## Summary
Severity: Medium
Advisory: JLSEC-2026-684
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-684
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.7.2+0

## Details
A malicious TLS1.2 server can force a TLS1.3 client with downgrade capability to use a ciphersuite that it did not agree to and achieve a successful connection. This is because, aside from the extensions, the client was skipping fully parsing the server hello.  https://doi.org/10.46586/tches.v2024.i1.457-500

## References
- https://github.com/advisories/GHSA-8cr7-x5g8-m3f3
- https://github.com/wolfSSL/wolfssl/blob/master/ChangeLog.md#add_later
- https://nvd.nist.gov/vuln/detail/CVE-2024-5814

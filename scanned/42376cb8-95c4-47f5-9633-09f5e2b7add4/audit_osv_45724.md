# [M] Issue summary: The 'openssl dgst' command-line tool silently truncates input data to 16MB when using...

## Summary
Severity: Medium
Advisory: JLSEC-2026-258
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-258
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.5+0

## Details
Issue summary: The 'openssl dgst' command-line tool silently truncates input
data to 16MB when using one-shot signing algorithms and reports success instead
of an error.

Impact summary: A user signing or verifying files larger than 16MB with
one-shot algorithms (such as Ed25519, Ed448, or ML-DSA) may believe the entire
file is authenticated while trailing data beyond 16MB remains unauthenticated.

When the 'openssl dgst' command is used with algorithms that only support
one-shot signing (Ed25519, Ed448, ML-DSA-44, ML-DSA-65, ML-DSA-87), the input
is buffered with a 16MB limit. If the input exceeds this limit, the tool
silently truncates to the first 16MB and continues without signaling an error,
contrary to what the documentation states. This creates an integrity gap where
trailing bytes can be modified without detection if both signing and
verification are performed using the same affected codepath.

The issue affects only the command-line tool behavior. Verifiers that process
the full message using library APIs will reject the signature, so the risk
primarily affects workflows that both sign and verify with the affected
'openssl dgst' command. Streaming digest algorithms for 'openssl dgst' and
library users are unaffected.

The FIPS modules in 3.5 and 3.6 are not affected by this issue, as the
command-line tools are outside the OpenSSL FIPS module boundary.

OpenSSL 3.5 and 3.6 are vulnerable to this issue.

OpenSSL 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are not affected by this issue.

## References
- https://github.com/advisories/GHSA-v2vr-926q-29fr
- https://github.com/openssl/openssl/commit/310f305eb92ea8040d6b3cb75a5feeba8e6acf2f
- https://github.com/openssl/openssl/commit/a7936fa4bd23c906e1955a16a0a0ab39a4953a61
- https://nvd.nist.gov/vuln/detail/CVE-2025-15469
- https://openssl-library.org/news/secadv/20260127.txt

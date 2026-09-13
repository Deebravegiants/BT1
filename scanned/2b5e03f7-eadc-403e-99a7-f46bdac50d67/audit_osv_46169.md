# [M] The PKCS#7 decode path ignores the caller-supplied output buffer size (outputSz), allowing decoded...

## Summary
Severity: Medium
Advisory: JLSEC-2026-754
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-754
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
The PKCS#7 decode path ignores the caller-supplied output buffer size (outputSz), allowing decoded content to be written past the bounds of the provided buffer. This affects wolfSSL 5.9.0 and earlier and was fixed in the 5.9.1 release.

## References
- https://github.com/advisories/GHSA-6q89-vxvr-wgv2
- https://github.com/wolfSSL/wolfssl/pull/10116
- https://nvd.nist.gov/vuln/detail/CVE-2026-6681
- https://www.wolfssl.com/docs/security-vulnerabilities
- https://www.wolfssl.com/docs/security-vulnerabilities/

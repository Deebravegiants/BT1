# [H] Protobuf: Denial of Service issue through malicious messages containing negative varints or deep recursion

## Summary
Severity: High
Advisory: GHSA-p2gh-cfq4-4wjc
CVE: CVE-2026-6409
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-p2gh-cfq4-4wjc
Type: github-advisory

## Affected
- Packagist: `google/protobuf` — affected >=0 <4.33.6

## Details
### Impact
A Denial of Service (DoS) vulnerability exists in the Protobuf PHP library during the parsing of untrusted input. Maliciously structured messages—specifically those containing negative `varint`s or deep recursion—can be used to crash the application, impacting service availability.

### Patches
Patches have been released to 5.34.0-RC1 and 4.33.6.

## References
- https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-p2gh-cfq4-4wjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-6409
- https://github.com/protocolbuffers/protobuf/issues/24159
- https://github.com/protocolbuffers/protobuf/issues/25067
- https://github.com/protocolbuffers/protobuf/commit/60e93d2d104f2af9cd345b1c6f3891d91430244a
- https://github.com/protocolbuffers/protobuf/commit/c8e9b27d95c6ab2d0668b5889e7dac2c477b7038
- https://github.com/protocolbuffers/protobuf

# [M] package pkcs12: Authentication bypass in Decode functions

## Summary
Severity: Medium
Advisory: GHSA-mpwr-8vm7-h73f
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-mpwr-8vm7-h73f
Type: github-advisory

## Affected
- Go: `software.sslmate.com/src/go-pkcs12` — affected >=0.6.0 <0.7.2

## Details
`Decode`, `DecodeChain`, `DecodeTrustStore`, and `ToPEM` can incorrectly accept PKCS#12 files which were encoded with the wrong password, due to a failure to reject excessively-short PBMAC1 keys. Users who decode PKCS#12 files from untrusted sources and rely on the password for authentication can be tricked into accepting malicious PKCS#12 files. Users who only decode PKCS#12 files from trusted sources are not affected.

Thanks to Pavol Žáčik (Red Hat) and Alex Gaynor (Anthropic) for finding and reporting the same issue in OpenSSL ([CVE-2026-34181](https://openssl-library.org/news/vulnerabilities/#CVE-2026-34181)).

## References
- https://github.com/SSLMate/go-pkcs12/security/advisories/GHSA-mpwr-8vm7-h73f
- https://github.com/SSLMate/go-pkcs12
- https://openssl-library.org/news/vulnerabilities/#CVE-2026-34181

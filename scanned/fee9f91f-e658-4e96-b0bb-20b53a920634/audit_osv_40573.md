# [M] libgit2: Inverted IP SubjectAltName Comparison in OpenSSL Backend

## Summary
Severity: Medium
Advisory: CVE-2026-53583
Aliases: GHSA-h7gc-w2gg-p9xp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-53583
Type: osv

## Details
libgit2 is a portable C implementation of the Git core methods provided as a linkable library with a solid API, allowing to build Git functionality into your application. Prior to 1.8.6 and 1.9.5, verify_server_cert in src/libgit2/streams/openssl.c uses an inverted !!memcmp result in the GEN_IPADD branch when comparing an IP-literal host with a certificate IP SubjectAltName. OpenSSL builds reject matching IP addresses and accept mismatched IP addresses, allowing a network attacker with a CA-trusted certificate containing any IP SubjectAltName to intercept libgit2 connections to IP-literal HTTPS URLs. DNS SubjectAltName validation and non-OpenSSL TLS backends are not affected. This issue is fixed in versions 1.8.6 and 1.9.5.

## References
- https://github.com/libgit2/libgit2/releases/tag/v1.8.6
- https://github.com/libgit2/libgit2/releases/tag/v1.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53583.json
- https://github.com/libgit2/libgit2/security/advisories/GHSA-h7gc-w2gg-p9xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-53583
- https://github.com/libgit2/libgit2/commit/647dcb432980b84ede4cb5a008bbd1ccb4ead03d
- https://github.com/libgit2/libgit2/commit/c2aa35409ee0e6515df64da49750f13a0a42c47f
- https://github.com/libgit2/libgit2/commit/ef086bc3e4eedf62be38a910381aae24d49871ff

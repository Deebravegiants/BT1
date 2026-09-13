# [M] openCryptoki incorrectly calculates the buffer size in C_WrapKey with CKM_ECDH_AES_KEY_WRAP

## Summary
Severity: Medium
Advisory: CVE-2026-22791
Aliases: GHSA-26f5-3mwq-4wm7
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2026-22791
Type: osv

## Details
openCryptoki is a PKCS#11 library and tools for Linux and AIX. In 3.25.0 and 3.26.0, there is a heap buffer overflow vulnerability in the CKM_ECDH_AES_KEY_WRAP implementation allows an attacker with local access to cause out-of-bounds writes in the host process by supplying a compressed EC public key and invoking C_WrapKey. This can lead to heap corruption, or denial-of-service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22791.json
- https://github.com/opencryptoki/opencryptoki/security/advisories/GHSA-26f5-3mwq-4wm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-22791
- https://github.com/opencryptoki/opencryptoki/commit/785d7577e1477d12fbe235554e7e7b24f2de34b7
- https://github.com/opencryptoki/opencryptoki/commit/e37e9127deeeb7bf3c3c4d852c594256c57ec3a8

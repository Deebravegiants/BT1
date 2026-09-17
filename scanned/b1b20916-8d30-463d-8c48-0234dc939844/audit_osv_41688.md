# [M] PKCS#12 MAC verification uses attacker-controlled comparison length

## Summary
Severity: Medium
Advisory: CVE-2026-6329
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-6329
Type: osv

## Details
PKCS#12 MAC verification uses an attacker-controlled comparison length, weakening the integrity check on the MAC and allowing a mismatched MAC to be accepted. The PKCS#12 verify path compared the locally computed HMAC against the MAC parsed from the PKCS#12 structure using a length taken directly from the attacker-supplied input, without first verifying that it equals the length of the digest actually produced by the configured algorithm. A truncated or zero-length stored MAC could therefore be accepted, defeating the integrity protection of the MAC.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6329.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6329
- https://github.com/wolfSSL/wolfssl/pull/10192
- https://github.com/wolfSSL/wolfssl

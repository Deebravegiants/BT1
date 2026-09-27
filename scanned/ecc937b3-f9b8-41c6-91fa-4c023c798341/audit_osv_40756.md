# [M] Session Cache Restore — Arbitrary Free via Deserialized Pointer

## Summary
Severity: Medium
Advisory: CVE-2026-5507
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:H/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5507
Type: osv

## Details
When restoring a session from cache, a pointer from the serialized session data is used in a free operation without validation. An attacker who can poison the session cache could trigger an arbitrary free. Exploitation requires the ability to inject a crafted session into the cache and for the application to call specific session restore APIs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5507.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5507
- https://github.com/wolfSSL/wolfssl/pull/10088

# [H] Pkcs11-provider: side-channel proofing pkcs#1 1.5 paths

## Summary
Severity: High
Advisory: CVE-2023-6258
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-30
Source: https://osv.dev/vulnerability/CVE-2023-6258
Type: osv

## Details
A security vulnerability has been identified in the pkcs11-provider, which is associated with Public-Key Cryptography Standards (PKCS#11). If exploited successfully, this vulnerability could result in a Bleichenbacher-like security flaw, potentially enabling a side-channel attack on PKCS#1 1.5 decryption.

## References
- https://packages.fedoraproject.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6258.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6258
- https://bugzilla.redhat.com/show_bug.cgi?id=2251062
- https://github.com/latchset/pkcs11-provider/pull/308

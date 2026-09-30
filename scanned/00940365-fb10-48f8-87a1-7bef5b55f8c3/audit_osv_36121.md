# [M] libtpms returns wrong initialization vector when certain symmetric ciphers are used

## Summary
Severity: Medium
Advisory: CVE-2026-21444
Aliases: GHSA-7jxr-4j3g-p34f
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-02
Source: https://osv.dev/vulnerability/CVE-2026-21444
Type: osv

## Details
libtpms, a library that provides software emulation of a Trusted Platform Module, has a flaw in versions 0.10.0 and 0.10.1. The commonly used integration of libtpms with OpenSSL 3.x contained a vulnerability related to the returned IV (initialization vector) when certain symmetric ciphers were used. Instead of returning the last IV it returned the initial IV to the caller, thus weakening the subsequent encryption and decryption steps. The highest threat from this vulnerability is to data confidentiality. Version 0.10.2 fixes the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21444.json
- https://github.com/stefanberger/libtpms/security/advisories/GHSA-7jxr-4j3g-p34f
- https://nvd.nist.gov/vuln/detail/CVE-2026-21444
- https://github.com/stefanberger/libtpms/issues/541
- https://github.com/stefanberger/libtpms/commit/33c9ff074cb16c1841ce7d7f33643c17c426743a

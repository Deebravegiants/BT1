# [M] FreeRDP before 3.29.0 Denial of Service via smartcard cache

## Summary
Severity: Medium
Advisory: CVE-2026-67288
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67288
Type: osv

## Details
FreeRDP before 3.29.0 contains a null pointer dereference vulnerability in smartcard cache request decoders that accept NULL NDR pointers for LookupName in SCARD_IOCTL_READCACHEA and SCARD_IOCTL_WRITECACHEA operations. When smartcard emulation is enabled, attackers can send crafted smartcard cache requests with NULL lookup-name pointers to trigger strlen() on a null pointer, causing client process termination.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67288.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-ph3q-f9w8-7jf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67288
- https://www.vulncheck.com/advisories/freerdp-before-denial-of-service-via-smartcard-cache
- https://github.com/FreeRDP/FreeRDP/commit/5370fb26fbf034ecd11d3026b6ad639b5fff493f
- https://github.com/FreeRDP/FreeRDP/commit/f3b4347105114fe7453828736bea069999af319f
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-5wr6-8m8j-3h7f

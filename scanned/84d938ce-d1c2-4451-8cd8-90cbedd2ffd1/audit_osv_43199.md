# [M] FreeRDP before 3.30.0 Out-of-Bounds Read via Kerberos GSS Wrap-token EC

## Summary
Severity: Medium
Advisory: CVE-2026-72745
Aliases: CVE-2026-73242, GHSA-vv64-95pc-vj9v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72745
Type: osv

## Details
FreeRDP before 3.30.0 contains an out-of-bounds vulnerability in kerberos_DecryptMessage() (winpr/libwinpr/sspi/Kerberos/kerberos.c). The 16-bit EC (extra count) field of a peer-supplied GSS Wrap token (RFC 4121) is used directly in pointer arithmetic to locate the encrypted regions without being bounds-checked, while only RRC and the total buffer length are validated. A malicious peer (server or client) can supply a large EC value (up to 0xFFFF) during CredSSP/NLA authentication, moving the decrypt operation's base pointers past the end of the ~60-byte token buffer. Because the AES-CTS-HMAC enctypes decrypt in place before the HMAC integrity check, this results in an out-of-bounds read and in-place out-of-bounds write, potentially leading to information disclosure, memory corruption, or denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72745.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-vv64-95pc-vj9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-72745
- https://www.vulncheck.com/advisories/freerdp-before-out-of-bounds-read-via-kerberos-gss-wrap-token-ec

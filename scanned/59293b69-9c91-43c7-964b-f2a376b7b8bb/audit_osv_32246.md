# [H] CVE-2025-26519

## Summary
Severity: High
Advisory: CVE-2025-26519
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2025-02-14
Source: https://osv.dev/vulnerability/CVE-2025-26519
Type: osv

## Details
musl libc 0.9.13 through 1.2.5 before 1.2.6 has an out-of-bounds write vulnerability when an attacker can trigger iconv conversion of untrusted EUC-KR text to UTF-8.

## References
- http://www.openwall.com/lists/oss-security/2025/02/13/2
- http://www.openwall.com/lists/oss-security/2025/02/13/3
- http://www.openwall.com/lists/oss-security/2025/02/13/4
- http://www.openwall.com/lists/oss-security/2025/02/13/5
- http://www.openwall.com/lists/oss-security/2025/02/14/5
- http://www.openwall.com/lists/oss-security/2025/02/14/6
- https://git.musl-libc.org/cgit/musl/commit/?id=c47ad25ea3b484e10326f933e927c0bc8cded3da
- https://git.musl-libc.org/cgit/musl/commit/?id=e5adcd97b5196e29991b524237381a0202a60659
- https://www.openwall.com/lists/oss-security/2025/02/13/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26519.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26519

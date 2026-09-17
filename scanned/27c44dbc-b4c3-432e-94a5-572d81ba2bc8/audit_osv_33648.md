# [H] CVE-2025-4802

## Summary
Severity: High
Advisory: CVE-2025-4802
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-4802
Type: osv

## Details
Untrusted LD_LIBRARY_PATH environment variable vulnerability in the GNU C Library version 2.27 to 2.38 allows attacker controlled loading of dynamically shared library in statically compiled setuid binaries that call dlopen (including internal dlopen calls after setlocale or calls to NSS functions such as getaddrinfo).

## References
- http://www.openwall.com/lists/oss-security/2025/05/16/7
- http://www.openwall.com/lists/oss-security/2025/05/17/2
- https://lists.debian.org/debian-lts-announce/2025/05/msg00033.html
- https://sourceware.org/cgit/glibc/commit/?id=1e18586c5820e329f741d5c710275e165581380e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4802.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4802
- https://sourceware.org/bugzilla/show_bug.cgi?id=32976

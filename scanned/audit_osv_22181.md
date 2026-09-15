# [C] CVE-2022-23219

## Summary
Severity: Critical
Advisory: CVE-2022-23219
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2022-23219
Type: osv

## Details
The deprecated compatibility function clnt_create in the sunrpc module of the GNU C Library (aka glibc) through 2.34 copies its hostname argument on the stack without validating its length, which may result in a buffer overflow, potentially resulting in a denial of service or (if an application is not built with a stack protector enabled) arbitrary code execution.

## References
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23219.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23219
- https://security.gentoo.org/glsa/202208-24
- https://sourceware.org/bugzilla/show_bug.cgi?id=22542
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html

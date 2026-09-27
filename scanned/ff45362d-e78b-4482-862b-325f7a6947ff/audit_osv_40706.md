# [C] scanf %mc off-by-one heap buffer overflow

## Summary
Severity: Critical
Advisory: CVE-2026-5450
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-5450
Type: osv

## Details
Calling the scanf family of functions with a %mc (malloc'd character match) in the GNU C Library version 2.7 to version 2.43 with a format width specifier with an explicit width greater than 1024 could result in a one byte heap buffer overflow.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5450
- https://sourceware.org/bugzilla/show_bug.cgi?id=CVE-2026-5450
- https://inbox.sourceware.org/libc-announce/b11f0003-6ec1-4bd6-b9de-9e38a4efeca3@redhat.com/T/#u

# [M] gethostbyaddr and gethostbyaddr_r return invalid DNS hostnames

## Summary
Severity: Medium
Advisory: CVE-2026-4438
CVSS: 5.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-4438
Type: osv

## Details
Calling gethostbyaddr or gethostbyaddr_r with a configured nsswitch.conf that specifies the library's DNS backend in the GNU C library version 2.34 to version 2.43 could result in an invalid DNS hostname being returned to the caller in violation of the DNS specification.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4438.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4438
- https://sourceware.org/bugzilla/show_bug.cgi?id=34015

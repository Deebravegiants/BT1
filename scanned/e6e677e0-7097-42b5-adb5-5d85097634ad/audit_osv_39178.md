# [H] gethostbyaddr and gethostbyaddr_r may incorrectly handle DNS response

## Summary
Severity: High
Advisory: CVE-2026-4437
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-4437
Type: osv

## Details
Calling gethostbyaddr or gethostbyaddr_r with a configured nsswitch.conf that specifies the library's DNS backend in the GNU C Library version 2.34 to version 2.43 could, with a crafted response from the configured DNS server, result in a violation of the DNS specification that causes the application to treat a non-answer section of the DNS response as a valid answer.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4437.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4437
- https://sourceware.org/bugzilla/show_bug.cgi?id=34014

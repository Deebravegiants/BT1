# [C] BookStack before 26.05.4 Remote Code Execution via Book Cover

## Summary
Severity: Critical
Advisory: CVE-2026-82450
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82450
Type: osv

## Details
BookStack before 26.05.4 contains a remote code execution vulnerability in the portable ZIP import functionality that allows users with Import Content and Create Books permissions to upload a PHP polyglot file as a book cover. Attackers can bypass image extension validation by embedding a PHP file with a .php filename in the ZIP archive, which is stored in the public web root and executed by unauthenticated requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82450
- https://www.vulncheck.com/advisories/bookstack-before-26.05.4-remote-code-execution-via-book-cover
- https://github.com/BookStackApp/BookStack/commit/e210cc32e4cbb1efeae5c5c9d0fef8e3c6a752e6
- https://github.com/BookStackApp/BookStack

# [M] CVE-2023-26142

## Summary
Severity: Medium
Advisory: CVE-2023-26142
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N/E:P)
Published: 2023-09-12
Source: https://osv.dev/vulnerability/CVE-2023-26142
Type: osv

## Details
All versions of the package crow are vulnerable to HTTP Response Splitting when untrusted user input is used to build header values. Header values are not properly sanitized against CRLF Injection in the set_header and add_header functions. An attacker can add the \r\n (carriage return line feeds) characters to end the HTTP response headers and inject malicious content.

## References
- https://gist.github.com/dellalibera/9247769cc90ed96c0d72ddbcba88c65c
- https://security.snyk.io/vuln/SNYK-UNMANAGED-CROW-5665556
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26142.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26142

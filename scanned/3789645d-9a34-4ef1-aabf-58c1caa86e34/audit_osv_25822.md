# [H] DoS in lua-http library

## Summary
Severity: High
Advisory: CVE-2023-4540
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-4540
Type: osv

## Details
Improper Handling of Exceptional Conditions vulnerability in Daurnimator lua-http library allows Excessive Allocation and a denial of service (DoS) attack to be executed by sending a properly crafted request to the server. 
Such a request causes the program to enter an infinite loop. 

This issue affects lua-http: all versions before commit ddab283.

## References
- https://cert.pl/en/posts/2023/09/CVE-2023-4540/
- https://cert.pl/posts/2023/09/CVE-2023-4540/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4540.json
- https://https://cert.pl/en/posts/2023/09/CVE-2023-4540/
- https://nvd.nist.gov/vuln/detail/CVE-2023-4540
- https://github.com/daurnimator/lua-http/commit/ddab2835c583d45dec62680ca8d3cbde55e0bae6
- https://github.com/daurnimator/lua-http

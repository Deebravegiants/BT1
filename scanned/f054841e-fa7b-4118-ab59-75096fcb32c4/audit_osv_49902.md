# [H] CVE-2019-25355

## Summary
Severity: High
Advisory: CVE-2019-25355
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2019-25355
Type: osv

## Details
gSOAP 2.8 contains a directory traversal vulnerability that allows unauthenticated attackers to access system files by manipulating HTTP path traversal techniques. Attackers can retrieve sensitive files like /etc/passwd by sending crafted GET requests with multiple '../' directory traversal sequences.

## References
- https://www.genivia.com/
- https://www.genivia.com/products.html#gsoap
- https://www.vulncheck.com/advisories/genivia-gsoap-gsoap-path-traversal
- https://www.exploit-db.com/exploits/47653

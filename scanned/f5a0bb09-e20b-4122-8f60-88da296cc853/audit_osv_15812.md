# [H] CVE-2019-19886

## Summary
Severity: High
Advisory: CVE-2019-19886
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2019-19886
Type: osv

## Details
Trustwave ModSecurity 3.0.0 through 3.0.3 allows an attacker to send crafted requests that may, when sent quickly in large volumes, lead to the server becoming slow or unresponsive (Denial of Service) because of a flaw in Transaction::addRequestHeader in transaction.cc.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GWVUC54OPU7ICFYIXXVGQ5DOTMR4Z6ZY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JI3MNFRNUZD6RAJ5CPQZSUXQXDZ2K7IL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M7IIUNYIEZOWHRWWRVT3FR45MLE6HGDY/
- https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/modsecurity-denial-of-service-details-cve-2019-19886/

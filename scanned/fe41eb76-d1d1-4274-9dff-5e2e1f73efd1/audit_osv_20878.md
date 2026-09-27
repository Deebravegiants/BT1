# [M] CVE-2021-37936

## Summary
Severity: Medium
Advisory: CVE-2021-37936
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-11-18
Source: https://osv.dev/vulnerability/CVE-2021-37936
Type: osv

## Details
It was discovered that Kibana was not sanitizing document fields containing HTML snippets. Using this vulnerability, an attacker with the ability to write documents to an elasticsearch index could inject HTML. When the Discover app highlighted a search term containing the HTML, it would be rendered for the user.

## References
- https://discuss.elastic.co/t/elastic-stack-7-14-1-security-update/283077
- https://www.elastic.co/community/security/

# [H] CVE-2021-22140

## Summary
Severity: High
Advisory: CVE-2021-22140
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-22140
Type: osv

## Details
Elastic App Search versions after 7.11.0 and before 7.12.0 contain an XML External Entity Injection issue (XXE) in the App Search web crawler beta feature. Using this vector, an attacker whose website is being crawled by App Search could craft a malicious sitemap.xml to traverse the filesystem of the host running the instance and obtain sensitive files.

## References
- https://discuss.elastic.co/t/7-12-1-security-update/271433

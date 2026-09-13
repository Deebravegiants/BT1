# [M] CVE-2020-13795

## Summary
Severity: Medium
Advisory: CVE-2020-13795
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-13795
Type: osv

## Details
An issue was discovered in Navigate CMS through 2.8.7. It allows Directory Traversal because lib/packages/templates/template.class.php mishandles ../ and ..\ substrings.

## References
- http://packetstormsecurity.com/files/157940/Navigate-CMS-2.8.7-Directory-Traversal.html
- https://github.com/NavigateCMS/Navigate-CMS/commit/88b41c7665ac7181be063b7a541dded7b207d9e7

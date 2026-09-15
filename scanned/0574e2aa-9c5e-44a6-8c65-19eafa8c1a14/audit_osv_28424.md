# [C] MasaCMS SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-32640
Aliases: GHSA-24rr-gwx3-jhqc
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2024-32640
Type: osv

## Details
MASA CMS is an Enterprise Content Management platform based on open source technology. Versions prior to 7.4.5, 7.3.12, and 7.2.7 contain a SQL injection vulnerability in the `processAsyncObject` method that can result in remote code execution. Versions 7.4.5, 7.3.12, and 7.2.7 contain a fix for the issue.

## References
- https://www.seebug.org/vuldb/ssvid-99835
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32640.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-24rr-gwx3-jhqc
- https://nvd.nist.gov/vuln/detail/CVE-2024-32640
- https://github.com/MasaCMS/MasaCMS/commit/259fc6061d022d5025a3289a3f8de9852ad9c91d
- https://github.com/MasaCMS/MasaCMS/commit/280489e2d6c8daf5022fdb0225235462dd9d4534
- https://github.com/MasaCMS/MasaCMS/commit/3d6319b8775bb6438bc822d845926990511f5075
- https://github.com/Stuub/CVE-2024-32640-SQLI-MuraCMS
- https://projectdiscovery.io/blog/hacking-apple-with-sql-injection?ref=projectdiscovery-io-blog-newsletter

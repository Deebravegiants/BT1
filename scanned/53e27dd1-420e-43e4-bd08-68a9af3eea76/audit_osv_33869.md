# [H] CVE-2025-51991

## Summary
Severity: High
Advisory: CVE-2025-51991
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-20
Source: https://osv.dev/vulnerability/CVE-2025-51991
Type: osv

## Details
XWiki through version 17.3.0 is vulnerable to Server-Side Template Injection (SSTI) in the Administration interface, specifically within the HTTP Meta Info field of the Global Preferences Presentation section. An authenticated administrator can inject crafted Apache Velocity template code, which is rendered on the server side without proper validation or sandboxing. This enables the execution of arbitrary template logic, which may expose internal server information or, in specific configurations, lead to further exploitation such as remote code execution or sensitive data leakage. The vulnerability resides in improper handling of dynamic template rendering within user-supplied configuration fields.

## References
- https://github.com/malcxlmj/cve-writeups/blob/main/CVE-2025-51991.md
- https://xwiki.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51991.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51991

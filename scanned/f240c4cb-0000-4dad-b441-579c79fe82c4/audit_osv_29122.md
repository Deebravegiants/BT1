# [M] Denial of service in REXML

## Summary
Severity: Medium
Advisory: CVE-2024-39908
Aliases: GHSA-4xqq-m2hx-25v8
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2024-39908
Type: osv

## Details
REXML is an XML toolkit for Ruby. The REXML gem before 3.3.1 has some DoS vulnerabilities when it parses an XML that has many specific characters such as `<`, `0` and `%>`. If you need to parse untrusted XMLs, you many be impacted to these vulnerabilities. The REXML gem 3.3.2 or later include the patches to fix these vulnerabilities. Users are advised to upgrade. Users unable to upgrade should avoid parsing untrusted XML strings.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00011.html
- https://www.ruby-lang.org/en/news/2024/07/16/dos-rexml-cve-2024-39908
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39908.json
- https://github.com/ruby/rexml/security/advisories/GHSA-4xqq-m2hx-25v8
- https://nvd.nist.gov/vuln/detail/CVE-2024-39908
- https://security.netapp.com/advisory/ntap-20250117-0008/

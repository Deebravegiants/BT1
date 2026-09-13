# [M] PwnDoc Server-Side Template Injection vulnerability  - Sandbox Escape to RCE using custom filters

## Summary
Severity: Medium
Advisory: CVE-2024-55652
Aliases: GHSA-jw5r-6927-hwpc
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-55652
Type: osv

## Details
PenDoc is a penetration testing reporting application. Prior to commit 1d4219c596f4f518798492e48386a20c6e9a2fe6, an attacker can write a malicious docx template containing expressions that escape the JavaScript sandbox to execute arbitrary code on the system. An attacker who can control the contents of the template document is able to execute arbitrary code on the system. By default, only users with the `admin` role are able to create or update templates. Commit 1d4219c596f4f518798492e48386a20c6e9a2fe6 patches the issue.

## References
- https://github.com/pwndoc/pwndoc/blob/main/backend/src/lib/report-filters.js#L258-L260
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55652.json
- https://github.com/pwndoc/pwndoc/security/advisories/GHSA-jw5r-6927-hwpc
- https://nvd.nist.gov/vuln/detail/CVE-2024-55652
- https://github.com/pwndoc/pwndoc/commit/1d4219c596f4f518798492e48386a20c6e9a2fe6

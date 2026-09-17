# [M] NoneBot Potential Information Leak in User-Constructed Message Templates

## Summary
Severity: Medium
Advisory: GHSA-59j8-776v-xxxg
CVE: CVE-2024-21624
CWE: CWE-1336, CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-59j8-776v-xxxg
Type: github-advisory

## Affected
- PyPI: `nonebot2` — affected >=2.0.0a16 <2.2.0

## Details
### Impact
This security advisory pertains to a potential information leak (e.g., environment variables) in instances where developers utilize `MessageTemplate` and incorporate user-provided data into templates.

### Patches
The identified vulnerability has been remedied in fix #2509 and will be included in versions released after 2.1.3. Users are strongly advised to upgrade to these patched versions to safeguard against the vulnerability.

### Workarounds
A temporary workaround involves filtering underscores before incorporating user input into the message template.

### References
- [Pull Request #2509](https://github.com/nonebot/nonebot2/pull/2509)
- [CWE-1336](https://cwe.mitre.org/data/definitions/1336.html)

## References
- https://github.com/nonebot/nonebot2/security/advisories/GHSA-59j8-776v-xxxg
- https://nvd.nist.gov/vuln/detail/CVE-2024-21624
- https://github.com/nonebot/nonebot2/pull/2509
- https://github.com/nonebot/nonebot2/commit/b65b3b438c95894654fd9081139989c757bdc6c1
- https://github.com/nonebot/nonebot2
- https://github.com/pypa/advisory-database/tree/main/vulns/nonebot2/PYSEC-2024-37.yaml

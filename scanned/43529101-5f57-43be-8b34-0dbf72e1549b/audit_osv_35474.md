# [C] CVE-2025-9556

## Summary
Severity: Critical
Advisory: CVE-2025-9556
Aliases: GHSA-mgcj-g55g-rf6h
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-12
Source: https://osv.dev/vulnerability/CVE-2025-9556
Type: osv

## Details
Langchaingo supports the use of jinja2 syntax when parsing prompts, which is in turn parsed using the gonja library v1.5.3.
Gonja supports include and extends syntax to read files, which leads to a server side template injection vulnerability within langchaingo, allowing an attacker to insert a statement into a prompt to read the "etc/passwd" file.

## References
- https://www.kb.cert.org/vuls/id/949137
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9556.json
- https://github.com/tmc/langchaingo/security/advisories/GHSA-mgcj-g55g-rf6h
- https://nvd.nist.gov/vuln/detail/CVE-2025-9556
- https://github.com/tmc/langchaingo/pull/1348

# [H] Business Logic And Unrestricted Project Deletion Lead To Take Over the System in reNgine

## Summary
Severity: High
Advisory: CVE-2025-24968
Aliases: GHSA-3327-6x79-q396
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-24968
Type: osv

## Details
reNgine is an automated reconnaissance framework for web applications. An unrestricted project deletion vulnerability allows attackers with specific roles, such as `penetration_tester` or `auditor` to delete all projects in the system. This can lead to a complete system takeover by redirecting the attacker to the onboarding page, where they can add or modify users, including Sys Admins, and configure critical settings like API keys and user preferences. This issue affects all versions up to and including 2.20. Users are advised to monitor the project for future releases which address this issue. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24968.json
- https://github.com/yogeshojha/rengine/security/advisories/GHSA-3327-6x79-q396
- https://nvd.nist.gov/vuln/detail/CVE-2025-24968

# [C] ChurchCRM has unauthenticated RCE in its Install Wizard

## Summary
Severity: Critical
Advisory: CVE-2025-62521
Aliases: GHSA-m8jq-j3p9-2xf3
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-62521
Type: osv

## Details
ChurchCRM is an open-source church management system. Prior to version 5.21.0, a pre-authentication remote code execution vulnerability in ChurchCRM's setup wizard allows unauthenticated attackers to inject arbitrary PHP code during the initial installation process, leading to complete server compromise. The vulnerability exists in `setup/routes/setup.php` where user input from the setup form is directly concatenated into a PHP configuration template without any validation or sanitization. Any parameter in the setup form can be used to inject PHP code that gets written to `Include/Config.php`, which is then executed on every page load. This is more severe than typical authenticated RCE vulnerabilities because it requires no credentials and affects the installation process that administrators must complete. Version 5.21.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62521.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-m8jq-j3p9-2xf3
- https://nvd.nist.gov/vuln/detail/CVE-2025-62521

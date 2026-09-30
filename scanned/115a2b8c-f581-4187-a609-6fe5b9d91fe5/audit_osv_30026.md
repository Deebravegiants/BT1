# [C] Unchecked logrotate settings lead to arbitrary command execution

## Summary
Severity: Critical
Advisory: CVE-2024-49368
Aliases: GHSA-66m6-27r9-77vm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49368
Type: osv

## Details
Nginx UI is a web user interface for the Nginx web server. Prior to version 2.0.0-beta.36, when Nginx UI configures logrotate, it does not verify the input and directly passes it to exec.Command, causing arbitrary command execution. Version 2.0.0-beta.36 fixes this issue.

## References
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.0.0-beta.36
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-66m6-27r9-77vm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49368.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49368

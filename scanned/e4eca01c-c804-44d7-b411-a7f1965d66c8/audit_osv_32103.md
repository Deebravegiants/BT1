# [M] iTop Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-24026
Aliases: GHSA-9g7f-jmc3-rrmf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-24026
Type: osv

## Details
iTop is an web based IT Service Management tool. Versions prior to 3.2.1 are vulnerable to regular expression denial of service (ReDoS) that may, under some circumstances, affect iTop server. Version 3.2.1 doesn't use the affected variable in the regular expression. As a workaround, if iTop app_root_url is defined in the configuration file, then there is no possible way to exploit this ReDoS.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24026.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-9g7f-jmc3-rrmf
- https://nvd.nist.gov/vuln/detail/CVE-2025-24026

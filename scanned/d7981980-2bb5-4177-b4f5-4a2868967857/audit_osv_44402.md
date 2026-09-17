# [C] CVE-2026-8208

## Summary
Severity: Critical
Advisory: CVE-2026-8208
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-09
Source: https://osv.dev/vulnerability/CVE-2026-8208
Type: osv

## Details
Gibbon versions before v30.0.01 are affected by a local file inclusion vulnerability resulting in RCE by changing the report archive directory and forcing interpretation of a user provided .zip as PHP. Successful exploitation requires Teacher or higher privileges. Exploitation could result in compromise of the underlying web server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8208.json
- https://github.com/GibbonEdu/core/releases/tag/v30.0.01
- https://nvd.nist.gov/vuln/detail/CVE-2026-8208
- https://projectblack.io/blog/gibbon-v30-authenticated-sql-injection-and-rce/#local-file-inclusionthe-next-shiny-new-thing

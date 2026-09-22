# [M] Cacti SQL Injection vulnerability in lib/html_form_templates.php by reading dirty data stored in database

## Summary
Severity: Medium
Advisory: CVE-2024-31458
Aliases: GHSA-jrxg-8wh8-943x
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-31458
Type: osv

## Details
Cacti provides an operational monitoring and fault management framework. Prior to version 1.2.27, some of the data stored in `form_save()` function in `graph_template_inputs.php` is not thoroughly checked and is used to concatenate the SQL statement in `draw_nontemplated_fields_graph_item()` function from `lib/html_form_templates.php` , finally resulting in SQL injection. Version 1.2.27 contains a patch for the issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RBEOAFKRARQHTDIYSL723XAFJ2Q6624X/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31458.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-jrxg-8wh8-943x
- https://nvd.nist.gov/vuln/detail/CVE-2024-31458

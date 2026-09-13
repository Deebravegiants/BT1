# [H] CVE-2023-26876

## Summary
Severity: High
Advisory: CVE-2023-26876
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-21
Source: https://osv.dev/vulnerability/CVE-2023-26876
Type: osv

## Details
SQL injection vulnerability found in Piwigo v.13.5.0 and before allows a remote attacker to execute arbitrary code via the filter_user_id parameter to the admin.php?page=history&filter_image_id=&filter_user_id endpoint.

## References
- http://packetstormsecurity.com/files/172059/Piwigo-13.5.0-SQL-Injection.html
- https://gist.github.com/rodnt/a190d14d1715890d8df19bad58b90693
- https://piwigo.com
- https://www.tempest.com.br
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26876.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26876
- http://seclists.org/fulldisclosure/2023/Apr/13

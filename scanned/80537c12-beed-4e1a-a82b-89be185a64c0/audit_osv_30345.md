# [C] CVE-2024-51211

## Summary
Severity: Critical
Advisory: CVE-2024-51211
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-51211
Type: osv

## Details
SQL injection vulnerability exists in OS4ED openSIS-Classic Version 9.1, specifically in the resetuserinfo.php file. The vulnerability is due to improper input validation of the $username_stn_id parameter, which can be manipulated by an attacker to inject arbitrary SQL commands.

## References
- https://github.com/kutsa1/My-CVE/tree/main/CVE-2024-51211
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51211.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51211

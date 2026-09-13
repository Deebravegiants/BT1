# [C] CVE-2019-5886

## Summary
Severity: Critical
Advisory: CVE-2019-5886
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/CVE-2019-5886
Type: osv

## Details
An issue was discovered in ShopXO 1.2.0. In the application\install\controller\Index.php file, there is no validation lock file in the Add method, which allows an attacker to reinstall the database. The attacker can write arbitrary code to database.php during system reinstallation.

## References
- https://github.com/gongfuxiang/shopxo/issues/1

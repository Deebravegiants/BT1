# [H] CVE-2020-24849

## Summary
Severity: High
Advisory: CVE-2020-24849
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-05
Source: https://osv.dev/vulnerability/CVE-2020-24849
Type: osv

## Details
A remote code execution vulnerability is identified in FruityWifi through 2.4. Due to improperly escaped shell metacharacters obtained from the POST request at the page_config_adv.php page, it is possible to perform remote code execution by an authenticated attacker. This is similar to CVE-2018-17317.

## References
- http://fruitywifi.com/index_eng.html
- https://github.com/xtr4nge/FruityWifi
- https://gist.github.com/harsh-bothra/f899045b16bbba264628d79d52c07c22

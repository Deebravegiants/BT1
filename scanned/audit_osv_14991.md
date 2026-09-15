# [H] CVE-2019-12839

## Summary
Severity: High
Advisory: CVE-2019-12839
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-15
Source: https://osv.dev/vulnerability/CVE-2019-12839
Type: osv

## Details
In OrangeHRM 4.3.1 and before, there is an input validation error within admin/listMailConfiguration (txtSendmailPath parameter) that allows authenticated attackers to achieve arbitrary command execution.

## References
- https://github.com/orangehrm/orangehrm/pull/528
- https://ctrsec.io/index.php/2019/06/11/ace-orangehrm/

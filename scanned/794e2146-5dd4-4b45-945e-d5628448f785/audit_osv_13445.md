# [H] CVE-2018-19897

## Summary
Severity: High
Advisory: CVE-2018-19897
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19897
Type: osv

## Details
ThinkCMF X2.2.2 has SQL Injection via the function _listorders() in AdminbaseController.class.php and is exploitable with the manager privilege via the listorders[key][1] parameter in a Link listorders action.

## References
- https://github.com/thinkcmf/cmfx/issues/26

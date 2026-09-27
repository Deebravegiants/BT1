# [H] CVE-2017-12585

## Summary
Severity: High
Advisory: CVE-2017-12585
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-06
Source: https://osv.dev/vulnerability/CVE-2017-12585
Type: osv

## Details
SLiMS 8 Akasia through 8.3.1 has SQL injection in admin/AJAX_lookup_handler.php (tableName and tableFields parameters), admin/AJAX_check_id.php, and admin/AJAX_vocabolary_control.php. It can be exploited by remote authenticated librarian users.

## References
- https://github.com/slims/slims8_akasia/issues/47

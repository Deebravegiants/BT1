# [C] CVE-2018-1000869

## Summary
Severity: Critical
Advisory: CVE-2018-1000869
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000869
Type: osv

## Details
phpIPAM version 1.3.2 contains a CWE-89 vulnerability in /app/admin/nat/item-add-submit.php that can result in SQL Injection.. This attack appear to be exploitable via Rough user, exploiting the vulnerability to access information he/she does not have access to.. This vulnerability appears to have been fixed in 1.4.

## References
- https://github.com/phpipam/phpipam/commit/856b10ca85a24c04ed8651f4e13f867ec78a353d
- https://github.com/phpipam/phpipam/issues/2344

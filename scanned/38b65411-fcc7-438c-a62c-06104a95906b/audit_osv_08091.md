# [M] CVE-2016-10216

## Summary
Severity: Medium
Advisory: CVE-2016-10216
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-02-10
Source: https://osv.dev/vulnerability/CVE-2016-10216
Type: osv

## Details
An issue was discovered in IT ITems DataBase (ITDB) through 1.23. The vulnerability exists due to insufficient filtration of user-supplied data in the "value" HTTP POST parameter passed to the "itdb-1.23/js/DataTables-1.8.2/examples/examples_support/editable_ajax.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://github.com/sivann/itdb/issues/56

# [M] CVE-2019-9085

## Summary
Severity: Medium
Advisory: CVE-2019-9085
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-24
Source: https://osv.dev/vulnerability/CVE-2019-9085
Type: osv

## Details
Hoteldruid before v2.3.1 allows remote authenticated users to cause a denial of service (invoice-creation outage) via the n_file parameter to visualizza_contratto.php with invalid arguments (any non-numeric value), as demonstrated by the anno=2019&id_transazione=1&numero_contratto=1&n_file=a query string to visualizza_contratto.php.

## References
- http://www.hoteldruid.com/en/download.html
- https://metamorfosec.com/Files/Advisories/METS-2019-006-An_Invalid_Arguments_in_Hoteldruid_before_v2.3.1.txt

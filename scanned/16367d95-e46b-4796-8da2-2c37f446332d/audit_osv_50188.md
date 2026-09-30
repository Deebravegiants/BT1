# [M] CVE-2019-9084

## Summary
Severity: Medium
Advisory: CVE-2019-9084
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-07
Source: https://osv.dev/vulnerability/CVE-2019-9084
Type: osv

## Details
In Hoteldruid before 2.3.1, a division by zero was discovered in $num_tabelle in tab_tariffe.php (aka the numtariffa1 parameter) due to the mishandling of non-numeric values, as demonstrated by the /tab_tariffe.php?anno=[YEAR]&numtariffa1=1a URI. It could allow an administrator to conduct remote denial of service (disrupting certain business functions of the product).

## References
- http://www.hoteldruid.com/en/download.html
- https://metamorfosec.com/Files/Advisories/METS-2019-005-A_division_by_zero_in_Hoteldruid_before_v2.3.1.txt

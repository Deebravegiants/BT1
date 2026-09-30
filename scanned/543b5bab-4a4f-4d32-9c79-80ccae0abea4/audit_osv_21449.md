# [C] CVE-2021-4313

## Summary
Severity: Critical
Advisory: CVE-2021-4313
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-16
Source: https://osv.dev/vulnerability/CVE-2021-4313
Type: osv

## Details
A vulnerability was found in NethServer phonenehome. It has been rated as critical. This issue affects the function get_info/get_country_coor of the file server/index.php. The manipulation leads to sql injection. The identifier of the patch is 759c30b0ddd7d493836bbdf695cf71624b377391. It is recommended to apply a patch to fix this issue. The identifier VDB-218393 was assigned to this vulnerability.

## References
- https://vuldb.com/?ctiid.218393
- https://vuldb.com/?id.218393
- https://github.com/NethServer/nethserver-phonehome/commit/759c30b0ddd7d493836bbdf695cf71624b377391
- https://github.com/NethServer/nethserver-phonehome/pull/10

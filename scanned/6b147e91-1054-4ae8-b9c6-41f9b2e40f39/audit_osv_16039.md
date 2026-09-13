# [H] CVE-2019-25085

## Summary
Severity: High
Advisory: CVE-2019-25085
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-26
Source: https://osv.dev/vulnerability/CVE-2019-25085
Type: osv

## Details
A vulnerability was found in GNOME gvdb. It has been classified as critical. This affects the function gvdb_table_write_contents_async of the file gvdb-builder.c. The manipulation leads to use after free. It is possible to initiate the attack remotely. The name of the patch is d83587b2a364eb9a9a53be7e6a708074e252de14. It is recommended to apply a patch to fix this issue. The identifier VDB-216789 was assigned to this vulnerability.

## References
- https://vuldb.com/?ctiid.216789
- https://vuldb.com/?id.216789
- https://github.com/GNOME/gvdb/commit/d83587b2a364eb9a9a53be7e6a708074e252de14

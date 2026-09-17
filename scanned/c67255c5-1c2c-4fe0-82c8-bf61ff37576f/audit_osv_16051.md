# [C] CVE-2019-25100

## Summary
Severity: Critical
Advisory: CVE-2019-25100
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-08
Source: https://osv.dev/vulnerability/CVE-2019-25100
Type: osv

## Details
A vulnerability was found in happyman twmap. It has been declared as critical. Affected by this vulnerability is an unknown functionality of the file twmap3/data/ajaxCRUD/pointdata2.php. The manipulation of the argument id leads to sql injection. Upgrading to version v2.9_v4.31 is able to address this issue. The identifier of the patch is babbec79b3fa4efb3bd581ea68af0528d11bba0c. It is recommended to upgrade the affected component. The identifier VDB-217645 was assigned to this vulnerability.

## References
- https://github.com/happyman/twmap/releases/tag/v2.9_v4.31
- https://vuldb.com/?ctiid.217645
- https://vuldb.com/?id.217645
- https://github.com/happyman/twmap/issues/42
- https://github.com/happyman/twmap/commit/babbec79b3fa4efb3bd581ea68af0528d11bba0c

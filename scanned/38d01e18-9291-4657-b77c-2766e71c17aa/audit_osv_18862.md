# [M] CVE-2020-36626

## Summary
Severity: Medium
Advisory: CVE-2020-36626
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2020-36626
Type: osv

## Details
A vulnerability classified as critical has been found in Modern Tribe Panel Builder Plugin. Affected is the function add_post_content_filtered_to_search_sql of the file ModularContent/SearchFilter.php. The manipulation leads to sql injection. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 4528d4f855dbbf24e9fc12a162fda84ce3bedc2f. It is recommended to apply a patch to fix this issue. VDB-216738 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?id.216738
- https://github.com/moderntribe/panel-builder/commit/4528d4f855dbbf24e9fc12a162fda84ce3bedc2f
- https://github.com/moderntribe/panel-builder/pull/173

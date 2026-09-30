# [C] CVE-2018-25076

## Summary
Severity: Critical
Advisory: CVE-2018-25076
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-16
Source: https://osv.dev/vulnerability/CVE-2018-25076
Type: osv

## Details
A vulnerability classified as critical was found in Events Extension on BigTree. Affected by this vulnerability is the function getRandomFeaturedEventByDate/getUpcomingFeaturedEventsInCategoriesWithSubcategories/recacheEvent/searchResults of the file classes/events.php. The manipulation leads to sql injection. The patch is named 11169e48ab1249109485fdb1e0c9fca3d25ba01d. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-218395.

## References
- https://vuldb.com/?ctiid.218395
- https://vuldb.com/?id.218395
- https://github.com/timbuckingham/bigtree-events/commit/11169e48ab1249109485fdb1e0c9fca3d25ba01d

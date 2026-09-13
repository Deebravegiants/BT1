# [C] CVE-2016-15016

## Summary
Severity: Critical
Advisory: CVE-2016-15016
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-08
Source: https://osv.dev/vulnerability/CVE-2016-15016
Type: osv

## Details
A vulnerability was found in mrtnmtth joomla_mod_einsatz_stats up to 0.2. It has been classified as critical. This affects the function getStatsByType of the file helper.php. The manipulation of the argument year leads to sql injection. Upgrading to version 0.3 is able to address this issue. The identifier of the patch is 27c1b443cff45c81d9d7d926a74c76f8b6ffc6cb. It is recommended to upgrade the affected component. The identifier VDB-217653 was assigned to this vulnerability.

## References
- https://github.com/mrtnmtth/joomla_mod_einsatz_stats/releases/tag/v0.3
- https://vuldb.com/?ctiid.217653
- https://vuldb.com/?id.217653
- https://github.com/mrtnmtth/joomla_mod_einsatz_stats/commit/27c1b443cff45c81d9d7d926a74c76f8b6ffc6cb

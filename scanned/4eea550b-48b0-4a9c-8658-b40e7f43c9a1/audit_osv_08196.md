# [M] CVE-2016-15014

## Summary
Severity: Medium
Advisory: CVE-2016-15014
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2016-15014
Type: osv

## Details
A vulnerability has been found in CESNET theme-cesnet up to 1.x on ownCloud and classified as problematic. Affected by this vulnerability is an unknown functionality of the file cesnet/core/lostpassword/templates/resetpassword.php. The manipulation leads to insufficiently protected credentials. Attacking locally is a requirement. Upgrading to version 2.0.0 is able to address this issue. The identifier of the patch is 2b857f2233ce5083b4d5bc9bfc4152f933c3e4a6. It is recommended to upgrade the affected component. The identifier VDB-217633 was assigned to this vulnerability.

## References
- https://github.com/CESNET/theme-cesnet/releases/tag/2.0.0
- https://vuldb.com/?ctiid.217633
- https://vuldb.com/?id.217633
- https://github.com/CESNET/theme-cesnet/commit/2b857f2233ce5083b4d5bc9bfc4152f933c3e4a6
- https://github.com/CESNET/theme-cesnet/pull/1

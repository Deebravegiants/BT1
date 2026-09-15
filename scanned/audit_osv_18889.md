# [C] CVE-2020-36762

## Summary
Severity: Critical
Advisory: CVE-2020-36762
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2020-36762
Type: osv

## Details
A vulnerability was found in ONS Digital RAS Collection Instrument up to 2.0.27 and classified as critical. Affected by this issue is the function jobs of the file .github/workflows/comment.yml. The manipulation of the argument $COMMENT_BODY leads to os command injection. Upgrading to version 2.0.28 is able to address this issue. The name of the patch is dcaad2540f7d50c512ff2e031d3778dd9337db2b. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-234248.

## References
- https://github.com/ONSdigital/ras-collection-instrument/releases/tag/2.0.28
- https://vuldb.com/?id.234248
- https://vuldb.com/?ctiid.234248
- https://github.com/ONSdigital/ras-collection-instrument/commit/dcaad2540f7d50c512ff2e031d3778dd9337db2b
- https://github.com/ONSdigital/ras-collection-instrument/pull/199

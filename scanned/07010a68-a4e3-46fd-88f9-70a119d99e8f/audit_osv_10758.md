# [C] CVE-2017-20187

## Summary
Severity: Critical
Advisory: CVE-2017-20187
Aliases: GHSA-8pp6-5qpw-85g3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-05
Source: https://osv.dev/vulnerability/CVE-2017-20187
Type: osv

## Details
** UNSUPPORTED WHEN ASSIGNED ** A vulnerability was found in Magnesium-PHP up to 0.3.0. It has been classified as problematic. Affected is the function formatEmailString of the file src/Magnesium/Message/Base.php. The manipulation of the argument email/name leads to injection. Upgrading to version 0.3.1 is able to address this issue. The patch is identified as 500d340e1f6421007413cc08a8383475221c2604. It is recommended to upgrade the affected component. VDB-244482 is the identifier assigned to this vulnerability. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://github.com/floriangaerber/Magnesium-PHP/releases/tag/v0.3.1
- https://vuldb.com/?ctiid.244482
- https://vuldb.com/?id.244482
- https://github.com/floriangaerber/Magnesium-PHP/commit/500d340e1f6421007413cc08a8383475221c2604

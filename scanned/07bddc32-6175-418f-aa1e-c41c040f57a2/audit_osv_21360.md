# [M] CVE-2021-4241

## Summary
Severity: Medium
Advisory: CVE-2021-4241
Aliases: GHSA-hc4j-7mqg-cxjj
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-11-15
Source: https://osv.dev/vulnerability/CVE-2021-4241
Type: osv

## Details
A vulnerability, which was classified as problematic, was found in phpservermon. Affected is the function setUserLoggedIn of the file src/psm/Service/User.php. The manipulation leads to use of predictable algorithm in random number generator. The exploit has been disclosed to the public and may be used. The name of the patch is bb10a5f3c68527c58073258cb12446782d223bc3. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-213744.

## References
- https://vuldb.com/?id.213744
- https://github.com/phpservermon/phpservermon/commit/bb10a5f3c68527c58073258cb12446782d223bc3
- https://huntr.dev/bounties/1-phpservermon/phpservermon/

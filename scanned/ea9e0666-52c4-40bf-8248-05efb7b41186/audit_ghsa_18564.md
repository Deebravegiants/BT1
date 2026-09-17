# [H] HAX CMS API Lacks Authorization Checks

## Summary
Severity: High
Advisory: GHSA-9jr9-8ff3-m894
CVE: CVE-2025-54378
CWE: CWE-285, CWE-862
Ecosystem: Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2025-07-25
Source: https://github.com/advisories/GHSA-9jr9-8ff3-m894
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.14
- Packagist: `elmsln/haxcms` — affected >=0 <11.0.14

## Details
### Summary

The HAX CMS API endpoints do not perform authorization checks when interacting with a resource. Both the JS and PHP versions of the CMS do not verify that a user has permission to interact with a resource before performing a given operation.

### Details

The API endpoints within the HAX CMS application check if a user is authenticated, but don't check for authorization before performing an operation.

#### Affected Resources

- [Operations.php: 760](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L760) `createNode()`
- [Operations.php: 868](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L868) `saveNode()`
- [Operations.php: 1171](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L1171) `deleteNode()`
- [Operations.php: 1789](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L1789) `listSites()`
- [Operations.php: 1890](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L1890) `createSite()`
- [Operations.php: 2196](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L2195) `getConfig()`
- [Operations.php: 2389](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L2389) `cloneSite()`
- [Operations.php: 2467](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L2467) `deleteSite()`
- [Operations.php: 2524](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L2524) `downloadSite()`
- [Operations.php: 2607](https://github.com/haxtheweb/haxcms-php/blob/b158d8ba1f9602af92ab084fd03b418f953079fd/system/backend/php/lib/Operations.php#L2606) `archiveSite()`


_Note: This may not include all affected endpoints within the application._

### Impact

An authenticated attacker can make requests to interact with other users' sites. This can be used to enumerate, modify, and delete other users' sites and nodes.

Additionally, an authenticated attacker can use the 'getConfig' endpoint to pull the application's configuration, which may store cleartext credentials.

### PoC - /deleteNode

1. Browse to the 'site.json' file for a target site, and note the ID of the item to delete.

![image](https://github.com/user-attachments/assets/84f8b396-876e-402b-b252-86d6cdec66c0)

2. Make a POST request to the 'deleteNode' endpoint with a valid JWT and the target object ID.

![image](https://github.com/user-attachments/assets/750f6b2b-ad57-4230-8fd9-05100c25cef5)

Site before editing:

![image](https://github.com/user-attachments/assets/b7482b53-fc12-4aca-a135-082f1751d4a2)

Site after editing:

![image](https://github.com/user-attachments/assets/5a982f70-d8ef-4523-bcdc-da2b5aa7f019)

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-9jr9-8ff3-m894
- https://nvd.nist.gov/vuln/detail/CVE-2025-54378
- https://github.com/haxtheweb/haxcms-nodejs/commit/5826e9b7f3d8c7c7635411768b86b199fad36969
- https://github.com/haxtheweb/haxcms-php/commit/24d30222481ada037597c4d7c0a51a1ef7af6cfd

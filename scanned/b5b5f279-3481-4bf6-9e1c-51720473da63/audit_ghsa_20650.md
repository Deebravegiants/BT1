# [H] DSpace ItemImportService API Vulnerable to Path Traversal in Simple Archive Format Package Import

## Summary
Severity: High
Advisory: GHSA-8rmh-55h4-93h5
CVE: CVE-2022-31195
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-8rmh-55h4-93h5
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-api` — affected >=4.0 <5.11
- Maven: `org.dspace:dspace-api` — affected >=6.0 <6.4

## Details
### Impact
ItemImportServiceImpl is vulnerable to a path traversal vulnerability. This means a malicious SAF (simple archive format) package could cause a file/directory to be created anywhere the Tomcat/DSpace user can write to on the server.  However, this path traversal vulnerability is only possible by a user with special privileges (either Administrators or someone with command-line access to the server).  This vulnerability impacts the XMLUI, JSPUI and command-line.

_This vulnerability does NOT impact 7.x._

### Patches

_DSpace 6.x:_ 
* Fixed in 6.4 via commit: https://github.com/DSpace/DSpace/commit/7af52a0883a9dbc475cf3001f04ed11b24c8a4c0
* 6.x patch file: https://github.com/DSpace/DSpace/commit/7af52a0883a9dbc475cf3001f04ed11b24c8a4c0.patch (may be applied manually if an immediate upgrade to 6.4 or 7.x is not possible)

_DSpace 5.x:_
* Fixed in 5.11 via commit: https://github.com/DSpace/DSpace/commit/56e76049185bbd87c994128a9d77735ad7af0199
* 5.x patch file: https://github.com/DSpace/DSpace/commit/56e76049185bbd87c994128a9d77735ad7af0199.patch (may be applied manually if an immediate upgrade to 5.11 or 6.4 or 7.x is not possible)

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### Workarounds

As a basic workaround, you may block all access to the following URL paths:
* If you are using the XMLUI, block all access to `/admin/batchimport` path (this is the URL of the Admin Batch Import tool). Keep in mind, if your site uses the path "/xmlui", then you'd need to block access to `/xmlui/admin/batchimport`.
* If you are using the JSPUI, block all access to `/dspace-admin/batchimport` path (this is the URL of the Admin Batch Import tool).  Keep in mind, if your site uses the path "/jspui", then you'd need to block access to `/jspui/dspace-admin/batchimport`.

Keep in mind, only an Administrative user or a user with command-line access to the server is able to import/upload SAF packages. Therefore, assuming those users do not blindly upload untrusted SAF packages, then it is unlikely your site could be impacted by this vulnerability.


### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-8rmh-55h4-93h5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31195
- https://github.com/DSpace/DSpace/commit/56e76049185bbd87c994128a9d77735ad7af0199
- https://github.com/DSpace/DSpace/commit/7af52a0883a9dbc475cf3001f04ed11b24c8a4c0
- https://github.com/DSpace/DSpace

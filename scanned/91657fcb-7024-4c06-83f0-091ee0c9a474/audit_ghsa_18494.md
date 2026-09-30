# [M] DSpace is vulnerable to Path Traversal attacks when importing packages using Simple Archive Format

## Summary
Severity: Medium
Advisory: GHSA-vhvx-8xgc-99wf
CVE: CVE-2025-53622
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-vhvx-8xgc-99wf
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-api` — affected >=0 <7.6.4
- Maven: `org.dspace:dspace-api` — affected >=8.0 <8.2
- Maven: `org.dspace:dspace-api` — affected >=9.0 <9.1

## Details
### Impact

A path traversal vulnerability is possible during the import of an archive (in [Simple Archive Format](https://wiki.lyrasis.org/pages/viewpage.action?pageId=104566653)), either from command-line (`./dspace import` command) or from the "Batch Import (Zip)" user interface feature.  _This vulnerability likely impacts all versions of DSpace 1.x <= 7.6.3, 8.0 <= 8.1, and 9.0_.

An attacker may craft a malicious Simple Archive Format (SAF) package where the `contents` file references any system files (using relative traversal sequences) which are readable by the Tomcat user.  If such a package is imported, this will result in sensitive content disclose, including retrieving arbitrary files or configurations from the server where DSpace is running.

**The Simple Archive Format (SAF) importer / Batch Import (Zip) is only usable by site administrators** (from user interface / REST API) or system administrators (from command-line).  Therefore, to exploit this vulnerability, the malicious payload would have to be provided by an attacker and trusted by an administrator (who would trigger the import).
* **The most severe practical impact** is a case where an attacker obtains DSpace administrator credentials and uses the Batch Import feature with a malicious SAF archive to expose sensitive local files readable by the Tomcat user.
* An attacker without administrative credentials might use some other tactic to convince an administrator to import a malicious SAF archive they have supplied.

### Patches

The fix is included in DSpace 7.6.4, 8.2 and 9.1. Please upgrade to one of these versions.

If you cannot upgrade immediately, it is possible to manually patch your DSpace backend. (No changes are necessary to the frontend.)  A pull request exists which can be used to patch systems running DSpace 7.6.x, 8.x or 9.0. This pull request provides validation checks of paths in the `contents` file of an SAF package to ensure it does not reference any files outside of the SAF package.
* Pull request for 7.x: https://github.com/DSpace/DSpace/pull/11036 ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/11036.patch))
* Pull request for 8.x: https://github.com/DSpace/DSpace/pull/11037 ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/11037.patch))
* Pull request for 9.0: https://github.com/DSpace/DSpace/pull/11038 ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/11038.patch))

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches to your DSpace backend as follows:
1. Download the appropriate patch file to the machine where DSpace backend is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace backend code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all newly built code to your installation directory). Depending on your setup you also may need to copy the updated "server" webapp over to your Tomcat webapps folder.
    3. Restart Tomcat (or runnable JAR)

### Workarounds
**Patching the system is the recommended fix.** It is not possible to fully protect your system via workarounds.

That said, until you are able to patch your system or upgrade, you can apply these best practices:
* Administrators must carefully inspect any SAF archives (they did not construct themselves) before importing, paying close attention to the `contents` file to validate it does not reference files outside of the SAF archives.
* If SAF archives are too large to manually inspect, you should avoid importing them until your site is patched.

### Credits
Discovered & reported by Marcin Miłosz (@MMilosz) of PCG Academia
Code fix developed by Marcin Miłosz of PCG Academia and Kim Shepherd (@kshepherd) of The Library Code

### For more information
* [Path Traversal Vulnerability explained](https://owasp.org/www-community/attacks/Path_Traversal)
* If you have any questions or comments about this advisory, please contact us at [security@dspace.org](mailto:security@dspace.org)

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-vhvx-8xgc-99wf
- https://nvd.nist.gov/vuln/detail/CVE-2025-53622
- https://github.com/DSpace/DSpace/pull/11036
- https://github.com/DSpace/DSpace/pull/11036.patch
- https://github.com/DSpace/DSpace/pull/11037
- https://github.com/DSpace/DSpace/pull/11037.patch
- https://github.com/DSpace/DSpace/pull/11038
- https://github.com/DSpace/DSpace/pull/11038.patch
- https://github.com/DSpace/DSpace

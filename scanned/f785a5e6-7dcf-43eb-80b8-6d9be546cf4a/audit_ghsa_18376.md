# [M] DSpace is vulnerable to XML External Entity injection during archive imports 

## Summary
Severity: Medium
Advisory: GHSA-jjwr-5cfh-7xwh
CVE: CVE-2025-53621
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-jjwr-5cfh-7xwh
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-api` — affected >=0 <7.6.4
- Maven: `org.dspace:dspace-api` — affected >=8.0 <8.2
- Maven: `org.dspace:dspace-api` — affected >=9.0 <9.1

## Details
### Impact

Two related XXE injection possibilities have been discovered, **impacting all versions of DSpace prior to 7.6.4, 8.2 and 9.1**.

1. External entities are not disabled when parsing XML files during import of an archive (in [Simple Archive Format](https://wiki.lyrasis.org/pages/viewpage.action?pageId=104566653)), either from command-line (`./dspace import` command) or from the "Batch Import (Zip)" user interface feature.  _(Likely impacts all versions of DSpace 1.x <= 7.6.3, 8.0 <= 8.1, and 9.0)_
2. External entities are also not explicitly disabled when parsing XML responses from some upstream services (ArXiv, Crossref, OpenAIRE, Creative Commons) used in [import from external sources](https://wiki.lyrasis.org/pages/viewpage.action?pageId=104566672) via the user interface or REST API. _(Impacts all versions of DSpace 7.0 <= 7.6.3, 8.0 <= 8.1 and 9.0)_

An XXE injection in these files may result in a connection being made to an attacker's site or a local path readable by the Tomcat user, with content potentially being injected into a metadata field. In the latter case, this may result in sensitive content disclosure, including retrieving arbitrary files or configurations from the server where DSpace is running or content from remote URLs. The ability to include content from a remote URL could result in a request forgery attack, and disclosure of sensitive information in the  response.

**The Simple Archive Format (SAF) importer / Batch Import (Zip) is only usable by site administrators** (from user interface / REST API) or system administrators (from command-line).  Therefore, to exploit this vulnerability, the malicious payload would have to be provided by an attacker and trusted by an administrator (who would trigger the import).
* **The most severe practical impact** is a case where an attacker obtains DSpace administrator credentials and uses the Batch Import feature with a malicious SAF archive to expose sensitive local files readable by the Tomcat user, or secrets and access tokens from an authenticated service via request forgery.
* An attacker without administrative credentials might use some other tactic to convince an administrator to import a malicious SAF archive they have supplied.

**The Import from External Sources feature has a narrower attack vector**.  While this feature is usable by any DSpace Submitter, the malicious payload must be provided *by the external source* (e.g. arXiv, Crossref, OpenAIRE, or Creative Commons).  No known method exists for an attacker to inject XXE via content uploads. Instead, the service itself would need to be compromised in such a way that it would inject a malicious payload into its API response.

### Patches

The fix is included in DSpace 7.6.4, 8.2 and 9.1. Please upgrade to one of these versions.

If you cannot upgrade immediately, it is possible to manually patch your DSpace backend. (No changes are necessary to the frontend.)  A pull request exists which can be used to patch systems running DSpace 7.6.x, 8.x or 9.0. This pull request provides central methods to retrieve Java XML, SAX, JAXB XML document builders with safe default settings, including XXE protection.
* Pull request for 7.x: https://github.com/DSpace/DSpace/pull/11032 ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/11032.patch))
* Pull request for 8.x: https://github.com/DSpace/DSpace/pull/11034 ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/11034.patch))
* Pull request for 9.0: https://github.com/DSpace/DSpace/pull/11035 ([Downloadable patch file](https://github.com/DSpace/DSpace/pull/11035.patch))

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
* Administrators must carefully inspect any SAF archives (they did not construct themselves) before importing.  If SAF archives are too large to manually inspect, you should avoid importing them until your site is patched.
* As necessary, affected external services can be disabled (see [documentation](https://wiki.lyrasis.org/pages/viewpage.action?pageId=104566672)) to mitigate the ability for a malicious payload to be delivered via external service APIs.


### Credits
Discovered & reported by Pablo Picurelli Ortiz (@superpegaso2703)
Code fix developed by Kim Shepherd (@kshepherd) of The Library Code

### For more information
* [XXE Cheat Sheet / Explanations](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
* If you have any questions or comments about this advisory, please contact us at [security@dspace.org](mailto:security@dspace.org)

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-jjwr-5cfh-7xwh
- https://nvd.nist.gov/vuln/detail/CVE-2025-53621
- https://github.com/DSpace/DSpace/pull/11032
- https://github.com/DSpace/DSpace/pull/11032.patch
- https://github.com/DSpace/DSpace/pull/11034
- https://github.com/DSpace/DSpace/pull/11034.patch
- https://github.com/DSpace/DSpace/pull/11035
- https://github.com/DSpace/DSpace/pull/11035.patch
- https://github.com/DSpace/DSpace

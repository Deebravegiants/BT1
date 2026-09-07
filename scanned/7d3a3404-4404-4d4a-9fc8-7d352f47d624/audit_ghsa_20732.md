# [H] JSPUI's controlled vocabulary feature vulnerable to Open Redirect before v6.4 and v5.11

## Summary
Severity: High
Advisory: GHSA-763j-q7wv-vf3m
CVE: CVE-2022-31193
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-763j-q7wv-vf3m
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-jspui` — affected >=4.0 <5.11
- Maven: `org.dspace:dspace-jspui` — affected >=6.0 <6.4

## Details
### Impact
The JSPUI controlled vocabulary servlet is vulnerable to an open redirect attack, where an attacker can craft a malicious URL that looks like a legitimate DSpace/repository URL.  When that URL is clicked by the target, it redirects them to a site of the attacker's choice.

_This vulnerability does NOT impact the XMLUI or 7.x._

### Patches
_DSpace 6.x:_
* Fixed in 6.x via commit: https://github.com/DSpace/DSpace/commit/f7758457b7ec3489d525e39aa753cc70809d9ad9
* 6.x patch file: https://github.com/DSpace/DSpace/commit/f7758457b7ec3489d525e39aa753cc70809d9ad9.patch (may be applied manually if an immediate upgrade to 6.4 or above is not possible)

_DSpace 5.x:_
* Fixed in 5.x via commit: https://github.com/DSpace/DSpace/commit/5f72424a478f59061dcc516b866dcc687bc3f9de
* 5.x patch file: https://github.com/DSpace/DSpace/commit/5f72424a478f59061dcc516b866dcc687bc3f9de.patch (may be applied manually if an immediate upgrade to 5.11 or 6,4 or above is not possible)

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### References
Discovered and reported by Johannes Moritz of Ripstech.

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-763j-q7wv-vf3m
- https://nvd.nist.gov/vuln/detail/CVE-2022-31193
- https://github.com/DSpace/DSpace/commit/5f72424a478f59061dcc516b866dcc687bc3f9de
- https://github.com/DSpace/DSpace/commit/f7758457b7ec3489d525e39aa753cc70809d9ad9
- https://github.com/DSpace/DSpace

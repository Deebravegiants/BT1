# [H] JSPUI spellcheck and autocomplete tools vulnerable to Cross Site Scripting

## Summary
Severity: High
Advisory: GHSA-c558-5gfm-p2r8
CVE: CVE-2022-31191
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-c558-5gfm-p2r8
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-jspui` — affected >=4.0 <5.11
- Maven: `org.dspace:dspace-jspui` — affected >=6.0 <6.4

## Details
### Impact
The JSPUI spellcheck "Did you mean" HTML escapes the data-spell attribute in the link, but not the actual displayed text.  Similarly, the JSPUI autocomplete HTML does not properly escape text passed to it. Both are vulnerable to XSS.  This vulnerability only impacts the JSPUI.

_This vulnerability does NOT impact the XMLUI or 7.x._

### Patches
_DSpace 6.x:_
* Fixed in 6.4 via two commits: 
    * Fix for spellcheck: https://github.com/DSpace/DSpace/commit/ebb83a75234d3de9be129464013e998dc929b68d
    * Fix for autocomplete: https://github.com/DSpace/DSpace/commit/35030a23e48b5946f5853332c797e1c4adea7bb7
* 6.x patch files available (may be applied manually if an immediate upgrade to 6.4 or above is not possible)
    * Fix for spellcheck: https://github.com/DSpace/DSpace/commit/ebb83a75234d3de9be129464013e998dc929b68d.patch
    * Fix for autocomplete: https://github.com/DSpace/DSpace/commit/35030a23e48b5946f5853332c797e1c4adea7bb7.patch

_DSpace 5.x:_
* Fixed in 5.11 via two commits: 
    * Fix for spellcheck: https://github.com/DSpace/DSpace/commit/c89e493e517b424dea6175caba54e91d3847fc3a
    * Fix for autocomplete: https://github.com/DSpace/DSpace/commit/6f75bb084ab1937d094208c55cd84340040bcbb5
* 5.x patch files available (may be applied manually if an immediate upgrade to 5.11 or 6.4 is not possible)
    * Fix for spellcheck: https://github.com/DSpace/DSpace/commit/c89e493e517b424dea6175caba54e91d3847fc3a.patch
    * Fix for autocomplete: https://github.com/DSpace/DSpace/commit/6f75bb084ab1937d094208c55cd84340040bcbb5.patch

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### References
Discovered & reported by Hassan Bhuiyan (Brunel University London)

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-c558-5gfm-p2r8
- https://nvd.nist.gov/vuln/detail/CVE-2022-31191
- https://github.com/DSpace/DSpace/commit/35030a23e48b5946f5853332c797e1c4adea7bb7
- https://github.com/DSpace/DSpace/commit/6f75bb084ab1937d094208c55cd84340040bcbb5
- https://github.com/DSpace/DSpace/commit/c89e493e517b424dea6175caba54e91d3847fc3a
- https://github.com/DSpace/DSpace/commit/ebb83a75234d3de9be129464013e998dc929b68d
- https://github.com/DSpace/DSpace

# [H] JSPUI Possible Cross Site Scripting in "Request a Copy" Feature

## Summary
Severity: High
Advisory: GHSA-4wm8-c2vv-xrpq
CVE: CVE-2022-31192
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-4wm8-c2vv-xrpq
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-jspui` — affected >=5.0 <5.11
- Maven: `org.dspace:dspace-jspui` — affected >=6.0 <6.4

## Details
### Impact
The JSPUI "Request a Copy" feature does not properly escape values submitted and stored from the "Request a Copy" form.  This means that item requests could be vulnerable to XSS attacks.  This vulnerability only impacts the JSPUI.

_This vulnerability does NOT impact the XMLUI or 7.x._

### Patches

_DSpace 6.x:_ 
* Fixed in 6.4 via commit: https://github.com/DSpace/DSpace/commit/503a6af57fd720c37b0d86c34de63baa5dd85819
* 6.x patch file: https://github.com/DSpace/DSpace/commit/503a6af57fd720c37b0d86c34de63baa5dd85819.patch (may be applied manually if an immediate upgrade to 6.4 is not possible)

_DSpace 5.x:_
* Fixed in 5.11 via commit: https://github.com/DSpace/DSpace/commit/28eb8158210d41168a62ed5f9e044f754513bc37
* 5.x patch file: https://github.com/DSpace/DSpace/commit/28eb8158210d41168a62ed5f9e044f754513bc37.patch (may be applied manually if an immediate upgrade to 5.11 or 6.4 is not possible)

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### Workarounds
As a workaround, you can temporarily disable the "Request a Copy" feature by either commenting out the below configuration (or setting its value to empty):
```
# Comment out this default value
# request.item.type = all
```
Once your JSPUI site is patched, you can re-enable this setting. See https://wiki.lyrasis.org/display/DSDOC6x/Request+a+Copy for more information on this setting.

### References
Discovered & reported by Andrea Bollini of 4Science

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-4wm8-c2vv-xrpq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31192
- https://github.com/DSpace/DSpace/commit/28eb8158210d41168a62ed5f9e044f754513bc37
- https://github.com/DSpace/DSpace/commit/f7758457b7ec3489d525e39aa753cc70809d9ad9
- https://github.com/DSpace/DSpace

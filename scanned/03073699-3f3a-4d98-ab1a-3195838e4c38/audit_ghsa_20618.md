# [M] XMLUI's metadata of withdrawn Items is exposed to anonymous users

## Summary
Severity: Medium
Advisory: GHSA-7w85-pp86-p4pq
CVE: CVE-2022-31190
CWE: CWE-200, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-7w85-pp86-p4pq
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-xmlui` — affected >=4.0 <6.4

## Details
### Impact
Metadata on a withdrawn Item is exposed via the XMLUI "mets.xml" object, as long as you know the handle/URL of the withdrawn Item. This vulnerability only impacts the XMLUI.

However, this vulnerability is very low severity as Item metadata does not tend to contain highly secure or sensitive information.

_This vulnerability does NOT impact the JSPUI or 7.x._

### Patches

Because of the low severity of this security issue, it requires updating to 6.4 to resolve.  _No patch is available for 5.x or below._

_DSpace 6.x:_
* Fixed in 6.4 via #2451 
* 6.x patch file: https://github.com/DSpace/DSpace/commit/574e25496a40173653ae7d0a49a19ed8e3458606.patch (may be applied manually if an immediate upgrade to 6.4 or above is not possible)

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### Workaround

If there are any withdrawn items which are known to have highly secure information in their metadata, they can be permanently deleted. This will ensure their secure metadata is inaccessible & removed from the system entirely.

### References
Discovered & reported by David Cavrenne of Atmire

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-7w85-pp86-p4pq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31190
- https://github.com/DSpace/DSpace/pull/2451
- https://github.com/DSpace/DSpace/commit/574e25496a40173653ae7d0a49a19ed8e3458606.patch
- https://github.com/DSpace/DSpace

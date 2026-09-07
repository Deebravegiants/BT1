# [M] JSPUI's "Internal System Error" page prints exceptions and stack traces without sanitization

## Summary
Severity: Medium
Advisory: GHSA-c2j7-66m3-r4ff
CVE: CVE-2022-31189
CWE: CWE-209
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-c2j7-66m3-r4ff
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-jspui` — affected >=4.0 <6.4

## Details
### Impact
When an "Internal System Error" occurs in the JSPUI, then entire exception (including stack trace) is available. Information in this stacktrace may be useful to an attacker in launching a more sophisticated attack.  This vulnerability only impacts the JSPUI.

_This vulnerability does NOT impact the XMLUI or 7.x._

### Patches

_DSpace 6.x:_
* Fixed in 6.4 via commit: https://github.com/DSpace/DSpace/commit/afcc6c3389729b85d5c7b0230cbf9aaf7452f31a
* 6.x patch file: https://github.com/DSpace/DSpace/commit/afcc6c3389729b85d5c7b0230cbf9aaf7452f31a.patch (may be applied manually if an immediate upgrade to 6.4 or above is not possible)

_DSpace 5.x:_
* The 6.x patch file can also be applied to an older 5.x installation.
* Alternatively, you can simply apply the workaround documented below.  The detailed error information embedded in `internal.jsp` is not necessary for the JSPUI to function.

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### Workarounds

The detailed error information embedded in `internal.jsp` is not necessary for the JSPUI to function.  Because this error information is also available in the `dspace.log` files, it does not need to be displayed in `internal.jsp`.

Modify your `internal.jsp`, and disable the display of the error message. This is most easily done by setting the returned exception to "null" at all times.  For example, add a new line between line number 43 and 44

```
// This line should exist around line number 43
Throwable ex = (Throwable) request.getAttribute("javax.servlet.error.exception");
// Add workaround for security issue. Ensure exception is always set to null.
ex = null;
// This line should exist around line number 44
if(ex == null) out.println("No stack trace available<br/>");
```

### References
Discovered & reported by Ozkan Erdogan (Brunel University London)

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-c2j7-66m3-r4ff
- https://nvd.nist.gov/vuln/detail/CVE-2022-31189
- https://github.com/DSpace/DSpace/commit/afcc6c3389729b85d5c7b0230cbf9aaf7452f31a
- https://github.com/DSpace/DSpace

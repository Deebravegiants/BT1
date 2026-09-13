# [H] JSPUI vulnerable to path traversal in submission (resumable) upload

## Summary
Severity: High
Advisory: GHSA-qp5m-c3m9-8q2p
CVE: CVE-2022-31194
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-qp5m-c3m9-8q2p
Type: github-advisory

## Affected
- Maven: `org.dspace:dspace-jspui` — affected >=4.0 <5.11
- Maven: `org.dspace:dspace-jspui` — affected >=6.0 <6.4

## Details
### Impact
The JSPUI resumable upload implementations in SubmissionController and FileUploadRequest are vulnerable to multiple path traversal attacks, allowing an attacker to create files/directories anywhere on the server writable by the Tomcat/DSpace user, by modifying some request parameters during submission. This path traversal can only be executed by a user with special privileges (submitter rights). This vulnerability only impacts the JSPUI.

_This vulnerability does NOT impact the XMLUI or 7.x._

### Patches

_DSpace 6.x:_
* Fixed in 6.4 via commit: https://github.com/DSpace/DSpace/commit/7569c6374aefeafb996e202cf8d631020eda5f24
* 6.x patch file: https://github.com/DSpace/DSpace/commit/7569c6374aefeafb996e202cf8d631020eda5f24.patch (may be applied manually if an immediate upgrade to 6.4 or above is not possible)

_DSpace 5.x:_
* Fixed in 5.11 via commit: https://github.com/DSpace/DSpace/commit/d1dd7d23329ef055069759df15cfa200c8e3
* 5.x patch file: https://github.com/DSpace/DSpace/commit/d1dd7d23329ef055069759df15cfa200c8e3.patch (may be applied manually if an immediate upgrade to 5.11 or 6.4 is not possible)

#### Apply the patch to your DSpace
If at all possible, we recommend upgrading your DSpace site based on the upgrade instructions. However, if you are unable to do so, you can manually apply the above patches as follows:
1. Download the appropriate patch file to the machine where DSpace is running
2. From the `[dspace-src]` folder, apply the patch, e.g. `git apply [name-of-file].patch`
3. Now, update your DSpace site (based loosely on the Upgrade instructions). This generally involves three steps:
    1. Rebuild DSpace, e.g. `mvn -U clean package`  (This will recompile all DSpace code)
    2. Redeploy DSpace, e.g. `ant update`  (This will copy all updated WARs / configs to your installation directory). Depending on your setup you also may need to copy the updated WARs over to your Tomcat webapps folder.
    3. Restart Tomcat

### Workarounds

There are no known workarounds. However, this vulnerability cannot be exploited by an anonymous user or a basic user. The user must first have submitter privileges to at least one Collection and be able to determine how to modify the request parameters to exploit the vulnerability.

### References
Discovered & reported by Johannes Moritz of Ripstech

### For more information
If you have any questions or comments about this advisory:
* Email us at security@dspace.org

## References
- https://github.com/DSpace/DSpace/security/advisories/GHSA-qp5m-c3m9-8q2p
- https://nvd.nist.gov/vuln/detail/CVE-2022-31194
- https://github.com/DSpace/DSpace/commit/7569c6374aefeafb996e202cf8d631020eda5f24
- https://github.com/DSpace/DSpace/commit/d1dd7d23329ef055069759df15cfa200c8e3
- https://github.com/DSpace/DSpace

# [C] Genie Path Traversal vulnerability via File Uploads

## Summary
Severity: Critical
Advisory: GHSA-wpcv-5jgp-69f3
CVE: CVE-2024-4701
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2024-05-09
Source: https://github.com/advisories/GHSA-wpcv-5jgp-69f3
Type: github-advisory

## Affected
- Maven: `com.netflix.genie:genie-web` — affected >=0 <4.3.18

## Details
### Overview
Path Traversal Vulnerability via  File Uploads in Genie 

### Impact
Any Genie OSS users running their own instance and relying on the filesystem to store file attachments submitted to the Genie application may be impacted. Using this technique, it is possible to write a file with any user-specified filename and file contents to any location on the file system that the Java process has write access - potentially leading to remote code execution (RCE).

Genie users who do not store these attachments locally on the underlying file system are not vulnerable to this issue. 

### Description
Genie's API accepts a multipart/form-data file upload which can be saved to a location on disk. However, it takes a user-supplied filename as part of the request and uses this as the filename when writing the file to disk. Since this filename is user-controlled, it is possible for a malicious actor to manipulate the filename in order to break out of the default attachment storage path and perform path traversal. 

Using this technique it is possible to write a file with any user specified name and file contents to any location on the file system that the Java process has write access to.

### Patches
This path traversal issue is fixed in Genie OSS v4.3.18. This issue was fixed in https://github.com/Netflix/genie/pull/1216 and  https://github.com/Netflix/genie/pull/1217 and a [new release](https://github.com/Netflix/genie/releases/tag/v4.3.18) with the fix was created. Please, upgrade your Genie OSS instances to the new version.

## References
- https://github.com/Netflix/genie/security/advisories/GHSA-wpcv-5jgp-69f3
- https://nvd.nist.gov/vuln/detail/CVE-2024-4701
- https://github.com/Netflix/genie/pull/1217
- https://github.com/Netflix/genie/commit/6bad017d8078c94e80d6c6fe8abd693910bf55cf
- https://github.com/Netflix/genie
- https://github.com/Netflix/genie/releases/tag/v4.3.18
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2024-001.md

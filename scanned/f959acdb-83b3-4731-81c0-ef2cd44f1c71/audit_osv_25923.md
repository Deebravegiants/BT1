# [H] Remote Code Execution in Eclipse RAP on Windows

## Summary
Severity: High
Advisory: CVE-2023-4760
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2023-09-21
Source: https://osv.dev/vulnerability/CVE-2023-4760
Type: osv

## Details
In Eclipse RAP versions from 3.0.0 up to and including 3.25.0, Remote Code Execution is possible on Windows when using the FileUpload component.






The reason for this is a not completely secure extraction of the file name in the FileUploadProcessor.stripFileName(String name) method. As soon as this finds a / in the path, everything before it is removed, but potentially \ (backslashes) coming further back are kept.

For example, a file name such as /..\..\webapps\shell.war can be used to upload a file to a Tomcat server under Windows, which is then saved as ..\..\webapps\shell.war in its webapps directory and can then be executed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4760.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4760
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/160
- https://github.com/eclipse-rap/org.eclipse.rap/pull/141

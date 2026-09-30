# [M] OutOfMemoryError for large multipart without filename in Eclipse Jetty

## Summary
Severity: Medium
Advisory: GHSA-qw69-rqj8-6qw8
CVE: CVE-2023-26048
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-04-19
Source: https://github.com/advisories/GHSA-qw69-rqj8-6qw8
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <9.4.51.v20230217
- Maven: `org.eclipse.jetty:jetty-server` — affected >=10.0.0 <10.0.14
- Maven: `org.eclipse.jetty:jetty-server` — affected >=11.0.0 <11.0.14

## Details
### Impact
Servlets with multipart support (e.g. annotated with `@MultipartConfig`) that call `HttpServletRequest.getParameter()` or `HttpServletRequest.getParts()` may cause `OutOfMemoryError` when the client sends a multipart request with a part that has a name but no filename and a very large content.

This happens even with the default settings of `fileSizeThreshold=0` which should stream the whole part content to disk.

An attacker client may send a large multipart request and cause the server to throw `OutOfMemoryError`.
However, the server may be able to recover after the `OutOfMemoryError` and continue its service -- although it may take some time.

A very large number of parts may cause the same problem.

### Patches
Patched in Jetty versions

* 9.4.51.v20230217 - via PR #9345
* 10.0.14 - via PR #9344
* 11.0.14 - via PR #9344

### Workarounds
Multipart parameter `maxRequestSize` must be set to a non-negative value, so the whole multipart content is limited (although still read into memory).
Limiting multipart parameter `maxFileSize` won't be enough because an attacker can send a large number of parts that summed up will cause memory issues.

### References
* https://github.com/eclipse/jetty.project/issues/9076
* https://github.com/jakartaee/servlet/blob/6.0.0/spec/src/main/asciidoc/servlet-spec-body.adoc#32-file-upload

## References
- https://github.com/eclipse/jetty.project/security/advisories/GHSA-qw69-rqj8-6qw8
- https://nvd.nist.gov/vuln/detail/CVE-2023-26048
- https://github.com/eclipse/jetty.project/issues/9076
- https://github.com/eclipse/jetty.project/pull/9344
- https://github.com/eclipse/jetty.project/pull/9345
- https://github.com/eclipse/jetty.project
- https://github.com/eclipse/jetty.project/releases/tag/jetty-9.4.51.v20230217
- https://github.com/jakartaee/servlet/blob/6.0.0/spec/src/main/asciidoc/servlet-spec-body.adoc#32-file-upload
- https://lists.debian.org/debian-lts-announce/2023/09/msg00039.html
- https://security.netapp.com/advisory/ntap-20230526-0001
- https://www.debian.org/security/2023/dsa-5507

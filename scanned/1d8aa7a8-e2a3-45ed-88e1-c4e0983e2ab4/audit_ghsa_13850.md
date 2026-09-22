# [M] StaticHandler disclosure of classpath resources on Windows when mounted on a wildcard route

## Summary
Severity: Medium
Advisory: GHSA-53jx-vvf9-4x38
CVE: CVE-2023-24815
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-53jx-vvf9-4x38
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-web` — affected >=4.0.0 <4.3.8

## Details
### Summary

When running vertx web applications that serve files using `StaticHandler` on Windows Operating Systems and Windows File Systems, if the mount point is a wildcard (`*`) then an attacker can exfiltrate any class path resource.


### Details
When computing the relative path to locate the resource, in case of wildcards, the code:

https://github.com/vert-x3/vertx-web/blob/62c0d66fa1c179ae6a4d57344631679a2b97e60f/vertx-web/src/main/java/io/vertx/ext/web/impl/Utils.java#L83

returns the user input (without validation) as the segment to lookup. Even though checks are performed to avoid escaping the sandbox, given that the input was not sanitized `\` are not properly handled and an attacker can build a path that is valid within the classpath.

### PoC

https://github.com/adrien-aubert-drovio/vertx-statichandler-windows-traversal-path-vulnerability

## References
- https://github.com/vert-x3/vertx-web/security/advisories/GHSA-53jx-vvf9-4x38
- https://nvd.nist.gov/vuln/detail/CVE-2023-24815
- https://github.com/vert-x3/vertx-web/commit/9e3a783b1d1a731055e9049078b1b1494ece9c15
- https://github.com/vert-x3/vertx-web
- https://github.com/vert-x3/vertx-web/blob/62c0d66fa1c179ae6a4d57344631679a2b97e60f/vertx-web/src/main/java/io/vertx/ext/web/impl/Utils.java#L83

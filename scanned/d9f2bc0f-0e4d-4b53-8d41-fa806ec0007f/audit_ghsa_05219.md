# [H] handlebars.java FileTemplateLoader Path Traversal

## Summary
Severity: High
Advisory: GHSA-r4gv-qr8j-p3pg
CVE: CVE-2026-55760
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-r4gv-qr8j-p3pg
Type: github-advisory

## Affected
- Maven: `com.github.jknack:handlebars` — affected >=0 <4.5.2

## Details
### Impact
Any application that passes user-controlled input to Handlebars.compile() using a FileTemplateLoader (or ClassPathTemplateLoader) is vulnerable to arbitrary file read. This is a realistic attack surface for web applications that use template names from URL path parameters, request parameters, or other user-controlled sources.

### Patches
com.github.jknack:handlebars:4.5.2

### Workarounds

Validate template name is derived from user input. 

```java
if (!file.getPath().startsWith(new File(prefix).getCanonicalPath())) {
        throw new IOException("Path traversal attempt detected: " + location);
}
```

## References
- https://github.com/jknack/handlebars.java/security/advisories/GHSA-r4gv-qr8j-p3pg
- https://github.com/jknack/handlebars.java

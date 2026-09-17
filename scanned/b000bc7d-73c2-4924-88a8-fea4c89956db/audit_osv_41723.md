# [H] Handlebars.java: Arbitrary file read in `SpringTemplateLoader` via URL-fragment suffix bypass

## Summary
Severity: High
Advisory: CVE-2026-63490
Aliases: GHSA-g29j-rwfv-h99w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63490
Type: osv

## Details
Handlebars.java provides logic-less and semantic Mustache templates with Java. Prior to 4.5.3, com.github.jknack.handlebars.springmvc.SpringTemplateLoader resolves attacker-influenced Spring MVC view names through Spring ResourceLoader without the path-containment validation used by other URL-based loaders. In handlebars-springmvc/src/main/java/com/github/jknack/handlebars/springmvc/SpringTemplateLoader.java, a view name using a file: or classpath: URL and ending with the # fragment delimiter places the appended .hbs suffix in the fragment, which FileUrlResource.exists() and URL.openStream() discard. HandlebarsViewResolver in handlebars-springmvc/src/main/java/com/github/jknack/handlebars/springmvc/HandlebarsViewResolver.java then passes the attacker-controlled name to handlebars.compile(), allowing an unauthenticated remote attacker to read files accessible to the JVM when an application exposes a controller with a user-influenced view name. This issue is fixed in version 4.5.3.

## References
- https://github.com/jknack/handlebars.java/releases/tag/v4.5.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63490.json
- https://github.com/jknack/handlebars.java/security/advisories/GHSA-g29j-rwfv-h99w
- https://nvd.nist.gov/vuln/detail/CVE-2026-63490
- https://github.com/jknack/handlebars.java/commit/61f43423a337b87db5fec1fe59f0725aaaa38df5

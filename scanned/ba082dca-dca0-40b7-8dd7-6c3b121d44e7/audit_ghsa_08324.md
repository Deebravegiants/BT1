# [C] Sandboxed Thymeleaf expressions vulnerable to improper recognition of unauthorized syntax patterns

## Summary
Severity: Critical
Advisory: GHSA-c9ph-gxww-7744
CVE: CVE-2026-41901
CWE: CWE-1336, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-c9ph-gxww-7744
Type: github-advisory

## Affected
- Maven: `org.thymeleaf:thymeleaf` — affected >=0 <3.1.5.RELEASE
- Maven: `org.thymeleaf:thymeleaf-spring5` — affected >=0 <3.1.5.RELEASE
- Maven: `org.thymeleaf:thymeleaf-spring6` — affected >=0 <3.1.5.RELEASE

## Details
### Impact

A security bypass vulnerability exists in the expression execution mechanisms of Thymeleaf up to and including 3.1.4.RELEASE. Although the library provides mechanisms to avoid the execution of potentially dangerous expressions in some specific sandboxed (restricted) contexts, it fails to properly neutralize specific constructs that allow this kind of expressions to be executed. If an application developer passes to the template engine unsanitized variables that contain such expressions, and these values are used in sandboxed contexts inside the templates, these expressions can be executed achieving Server-Side Template Injection (SSTI).

### Patches

This has been fixed in Thymeleaf 3.1.5.RELEASE. All users are advised to upgrade immediately.

### Workarounds

No workaround is available beyond ensuring applications do not pass unvalidated/unsanitized data directly to the template engine. Upgrading to 3.1.5.RELEASE is strongly recommended in any case.

## References
- https://github.com/thymeleaf/thymeleaf/security/advisories/GHSA-c9ph-gxww-7744
- https://nvd.nist.gov/vuln/detail/CVE-2026-41901
- https://github.com/thymeleaf/thymeleaf

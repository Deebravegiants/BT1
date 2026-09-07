# [C] Improper restriction of the scope of accessible objects in Thymeleaf expressions

## Summary
Severity: Critical
Advisory: GHSA-r4v4-5mwr-2fwr
CVE: CVE-2026-40477
CWE: CWE-1336, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-r4v4-5mwr-2fwr
Type: github-advisory

## Affected
- Maven: `org.thymeleaf:thymeleaf` — affected >=0 <3.1.4.RELEASE
- Maven: `org.thymeleaf:thymeleaf-spring5` — affected >=0 <3.1.4.RELEASE
- Maven: `org.thymeleaf:thymeleaf-spring6` — affected >=0 <3.1.4.RELEASE

## Details
### Impact
A security bypass vulnerability exists in the expression execution mechanisms of Thymeleaf up to and including 3.1.3.RELEASE. Although the library provides mechanisms to prevent expression injection, it fails to properly restrict the scope of accessible objects, allowing specific potentially sensitive objects to be reached from within a template. If an application developer passes unvalidated user input directly to the template engine, an unauthenticated remote attacker can bypass the library's protections to achieve Server-Side Template Injection (SSTI).

### Patches
This has been fixed in Thymeleaf 3.1.4.RELEASE.

### Workarounds
No workaround is available beyond ensuring applications do not pass unvalidated user input directly to the template engine. Upgrading to 3.1.4.RELEASE is strongly recommended in any case.


### Credits
Thanks to Thomas Reburn (Praetorian) for responsible disclosure.

## References
- https://github.com/thymeleaf/thymeleaf/security/advisories/GHSA-r4v4-5mwr-2fwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40477
- https://github.com/thymeleaf/thymeleaf

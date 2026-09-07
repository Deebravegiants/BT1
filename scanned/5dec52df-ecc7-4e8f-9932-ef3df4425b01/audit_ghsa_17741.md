# [M] HAL Console has a Cross Site Scripting (XSS) vulnerability of user input

## Summary
Severity: Medium
Advisory: GHSA-jhvj-f397-8w6q
CVE: CVE-2025-23366
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-jhvj-f397-8w6q
Type: github-advisory

## Affected
- Maven: `org.jboss.hal:hal-console` — affected >=0 <3.7.7.Final

## Details
A flaw was found in the HAL Console in the Wildfly component, which does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output used as a web page that is served to other users. The attacker must be authenticated as a user that belongs to management groups “SuperUser”, “Admin”, or “Maintainer”.

### Impact
Cross-site scripting (XSS) vulnerability in the management console.

### Patches
Fixed in [HAL 3.7.7.Final](https://github.com/hal/console/releases/tag/v3.7.7) 

### Workarounds
No workaround available

### References
- https://access.redhat.com/security/cve/CVE-2025-23366
- https://bugzilla.redhat.com/show_bug.cgi?id=2337619

## References
- https://github.com/hal/console/security/advisories/GHSA-jhvj-f397-8w6q
- https://access.redhat.com/security/cve/CVE-2025-23366
- https://bugzilla.redhat.com/show_bug.cgi?id=2337619
- https://github.com/hal/console
- https://github.com/hal/console/releases/tag/v3.7.7

# [H] GeoNetwork has reflected XSS through client-side template injection

## Summary
Severity: High
Advisory: GHSA-2v4m-fw6c-g78f
CVE: CVE-2026-39379
CWE: CWE-1336, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-2v4m-fw6c-g78f
Type: github-advisory

## Affected
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=3.0.0
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.0.0-alpha.1
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.2.0 <4.2.15
- Maven: `org.geonetwork-opensource:geonetwork` — affected >=4.4.0 <4.4.10

## Details
### Summary
It is possible to craft a URL that causes GeoNetwork to reflect attacker-controlled content into an error page in a way that gets evaluated as a client-side template expression. Combined with known AngularJS sandbox-escape techniques, this can be used to execute arbitrary JavaScript in the victim's browser (reflected Cross-Site Scripting via client-side template injection).

### Details
When a user requests a service URL that does not exist or that they are not authorized to access, GeoNetwork shows an error page that reflects part of the original request back to the user without adequately neutralizing it for the context it is rendered in. Because this error page is an AngularJS application, attacker-controlled content in the reflected value can be interpreted as a template expression and evaluated once the page loads in the victim's browser, rather than being displayed as inert text.

### Impact
An attacker can trick a user (including an administrator) into visiting a crafted link. The resulting script execution runs in the context of the victim's authenticated session and can be used to exfiltrate information or perform actions on the victim's behalf. For example, an attacker could inject a fake login form that looks identical to the legitimate GeoNetwork login page to harvest credentials.

GeoNetwork 3.x and 4.0.x are archived/unmaintained and will not receive a fix for this issue. Instances running those lines should upgrade to a supported release (4.2.15 or later, or 4.4.10 or later).

## References
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-2v4m-fw6c-g78f
- https://github.com/geonetwork/core-geonetwork

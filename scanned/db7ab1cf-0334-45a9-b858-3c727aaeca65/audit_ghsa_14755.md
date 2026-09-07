# [M] Cross Site Scripting (XSS) vulnerability while uploading content to a new deployment

## Summary
Severity: Medium
Advisory: GHSA-64gp-r758-8pfm
CWE: CWE-1395, CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-64gp-r758-8pfm
Type: github-advisory

## Affected
- Maven: `org.jboss.hal:hal-console` — affected >=0 <3.7.7.Final

## Details
A vulnerability was found in the WildFly management console. A user may perform cross-site scripting in the deployment system. An attacker (or insider) may execute a malicious payload which could trigger an undesired behavior against the server.

### Impact
Cross-site scripting (XSS) vulnerability in the management console.

### Patches
Fixed in [HAL 3.7.7.Final](https://github.com/hal/console/releases/tag/v3.7.7) 

### Workarounds
No workaround available

### References
See also: https://issues.redhat.com/browse/WFLY-19969

## References
- https://github.com/hal/console/security/advisories/GHSA-64gp-r758-8pfm
- https://github.com/hal/console
- https://github.com/hal/console/releases/tag/v3.7.7
- https://issues.redhat.com/browse/WFLY-19969

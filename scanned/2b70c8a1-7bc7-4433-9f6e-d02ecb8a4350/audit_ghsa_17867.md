# [H] Volto affected by possible DoS by invoking specific URL by anonymous user

## Summary
Severity: High
Advisory: GHSA-xjhf-7833-3pm5
CVE: CVE-2025-58047
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-xjhf-7833-3pm5
Type: github-advisory

## Affected
- npm: `@plone/volto` — affected >=0 <16.34.0
- npm: `@plone/volto` — affected >=17.0.0 <17.22.1
- npm: `@plone/volto` — affected >=18.0.0 <18.24.0
- npm: `@plone/volto` — affected >=19.0.0-alpha.1 <19.0.0-alpha.4

## Details
### Impact
When visiting a specific URL, an anonymous user could cause the NodeJS server part of Volto to quit with an error.

### Patches
The problem has been patched and the patch has been backported to Volto major versions down until 16. It is advised to upgrade to the latest patch release of your respective current major version:

- Volto 16: [16.34.0](https://github.com/plone/volto/releases/tag/16.34.0)
- Volto 17: [17.22.1](https://github.com/plone/volto/releases/tag/17.22.1)
- Volto 18: [18.24.0](https://github.com/plone/volto/releases/tag/18.24.0)
- Volto 19: [19.0.0-alpha4](https://github.com/plone/volto/releases/tag/19.0.0-alpha.4)

### Workarounds
Make sure your setup automatically restarts processes that quit with an error. This won't prevent a crash, but it minimises downtime.

### Report
The problem was discovered by FHNW, a client of Plone provider kitconcept, who shared it with the Plone Zope Security Team (security@plone.org).

## References
- https://github.com/plone/volto/security/advisories/GHSA-xjhf-7833-3pm5
- https://nvd.nist.gov/vuln/detail/CVE-2025-58047
- https://github.com/plone/volto/commit/2789a287ac45ad9039fb9161d465ba13241fff0a
- https://github.com/plone/volto
- https://github.com/plone/volto/releases/tag/16.34.0
- https://github.com/plone/volto/releases/tag/17.22.1
- https://github.com/plone/volto/releases/tag/18.24.0
- https://github.com/plone/volto/releases/tag/19.0.0-alpha.4
- http://www.openwall.com/lists/oss-security/2025/08/28/3

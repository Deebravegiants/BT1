# [H] Cross-Site Scripting vulnerability in @backstage/plugin-auth-backend

## Summary
Severity: High
Advisory: GHSA-w7fj-336r-vw49
CVE: CVE-2021-43776
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-w7fj-336r-vw49
Type: github-advisory

## Affected
- npm: `@backstage/plugin-auth-backend` — affected >=0 <0.4.9

## Details
### Impact
This vulnerability allows a malicious actor to trick another user into visiting a vulnerable URL that executes an XSS attack. This attack can potentially allow the attacker to exfiltrate access tokens or other secrets from the user's browser. The default CSP does prevent this attack, but it is expected that some deployments have these policies disabled due to incompatibilities.

### Patches
This is vulnerability is patched in version `0.4.9` of `@backstage/plugin-auth-backend`.

### For more information
If you have any questions or comments about this advisory:

* Open an issue in the [Backstage repository](https://github.com/backstage/backstage)
* Visit our chat, linked to in [Backstage README](https://github.com/backstage/backstage)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-w7fj-336r-vw49
- https://nvd.nist.gov/vuln/detail/CVE-2021-43776
- https://github.com/backstage/backstage
- https://github.com/backstage/backstage/tree/master/plugins/auth-backend

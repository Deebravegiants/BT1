# [H] Backstage has a Possible Symlink Path Traversal in Scaffolder Actions

## Summary
Severity: High
Advisory: GHSA-rq6q-wr2q-7pgp
CVE: CVE-2026-24046
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-rq6q-wr2q-7pgp
Type: github-advisory

## Affected
- npm: `@backstage/backend-defaults` — affected >=0 <0.12.2
- npm: `@backstage/backend-defaults` — affected >=0.13.0 <0.13.2
- npm: `@backstage/backend-defaults` — affected >=0.14.0 <0.14.1
- npm: `@backstage/plugin-scaffolder-backend` — affected >=0 <2.2.2
- npm: `@backstage/plugin-scaffolder-backend` — affected >=3.0.0 <3.0.2
- npm: `@backstage/plugin-scaffolder-backend` — affected >=3.1.0 <3.1.1
- npm: `@backstage/plugin-scaffolder-node` — affected >=0 <0.11.2
- npm: `@backstage/plugin-scaffolder-node` — affected >=0.12.0 <0.12.3

## Details
### Impact

Multiple Scaffolder actions and archive extraction utilities were vulnerable to symlink-based path traversal attacks. An attacker with access to create and execute Scaffolder templates could exploit symlinks to:

1. **Read arbitrary files** via the `debug:log` action by creating a symlink pointing to sensitive files (e.g., `/etc/passwd`, configuration files, secrets)
2. **Delete arbitrary files** via the `fs:delete` action by creating symlinks pointing outside the workspace
3. **Write files outside the workspace** via archive extraction (tar/zip) containing malicious symlinks

This affects any Backstage deployment where users can create or execute Scaffolder templates.

### Patches

This vulnerability is fixed in the following package versions:

- `@backstage/backend-defaults` version 0.12.2, 0.13.2, 0.14.1, 0.15.0
- `@backstage/plugin-scaffolder-backend` version 2.2.2, 3.0.2, 3.1.1
- `@backstage/plugin-scaffolder-node` version 0.11.2, 0.12.3

Users should upgrade to these versions or later.

### Workarounds

- Follow the recommendation in the [Backstage Threat Model](https://backstage.io/docs/overview/threat-model#scaffolder) to limit access to creating and updating templates
- Restrict who can create and execute Scaffolder templates using the permissions framework
- Audit existing templates for symlink usage
- Run Backstage in a containerized environment with limited filesystem access

### References

- [CWE-59: Improper Link Resolution Before File Access](https://cwe.mitre.org/data/definitions/59.html)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-rq6q-wr2q-7pgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-24046
- https://github.com/backstage/backstage/commit/c641c147ab371a9a8a2f5f67fdb7cb9c97ef345d
- https://github.com/backstage/backstage

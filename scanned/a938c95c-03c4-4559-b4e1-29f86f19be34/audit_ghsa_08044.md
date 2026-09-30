# [M] @backstage/plugin-techdocs-node vulnerable to possible Path Traversal in TechDocs Local Generator

## Summary
Severity: Medium
Advisory: GHSA-w669-jj7h-88m9
CVE: CVE-2026-25152
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-w669-jj7h-88m9
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs-node` — affected >=1.14.0 <1.14.1
- npm: `@backstage/plugin-techdocs-node` — affected >=0 <1.13.11

## Details
### Impact
A path traversal vulnerability in the TechDocs local generator allows attackers to read arbitrary files from the host filesystem when Backstage is configured with `techdocs.generator.runIn: local`.

When processing documentation from untrusted sources, symlinks within the docs directory are followed by MkDocs during the build process. File contents are embedded into generated HTML and exposed to users who can view the documentation.

### Patches
This vulnerability is fixed in` @backstage/plugin-techdocs-node` version X.X.X. Users should upgrade to this version or later.

### Workarounds
- Switch to `runIn: docker` in your `app-config.yaml`:
```yaml
  techdocs:
    generator:
      runIn: docker
```
  - Restrict write access to TechDocs source repositories to trusted users only

### References
- https://backstage.io/docs/features/techdocs/configuration

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-w669-jj7h-88m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-25152
- https://github.com/backstage/backstage/commit/08f388e3394b133171fe13b62a78caf14407b9c3
- https://github.com/backstage/backstage

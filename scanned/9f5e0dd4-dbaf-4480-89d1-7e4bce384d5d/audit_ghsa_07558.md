# [H] @backstage/plugin-techdocs-node vulnerable to arbitrary code execution via MkDocs hooks

## Summary
Severity: High
Advisory: GHSA-6jr7-99pf-8vgf
CVE: CVE-2026-25153
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-6jr7-99pf-8vgf
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs-node` — affected >=1.14.0 <1.14.1
- npm: `@backstage/plugin-techdocs-node` — affected >=0 <1.13.11

## Details
### Impact

When TechDocs is configured with `runIn: local`, a malicious actor who can submit or modify a repository's `mkdocs.yml` file can execute arbitrary Python code on the TechDocs build server via MkDocs hooks configuration.

### Patches

Upgrade to `@backstage/plugin-techdocs-node` version 1.13.11, 1.14.1 or later.
The fix introduces an allowlist of supported MkDocs configuration keys. Unsupported configuration keys (including `hooks`) are now removed from `mkdocs.yml` before running the generator, with a warning logged to indicate which keys were removed.

**Note**: Users of `@techdocs/cli` should also upgrade to the latest version, which includes the fixed `@backstage/plugin-techdocs-node` dependency.

### Workarounds

If you cannot upgrade immediately:

1. Use Docker mode with restricted access: Configure TechDocs with `runIn: docker` instead of `runIn: local`. This provides container isolation, though it does not fully mitigate the risk.
2. Restrict repository access: Limit who can modify `mkdocs.yml` files in repositories that TechDocs processes. Only allow trusted contributors.
3. Manual review: Implement PR review requirements for changes to `mkdocs.yml` files to detect malicious `hooks` configurations before they are merged.
4. Downgrade MkDocs: Use MkDocs < 1.4.0 (e.g., 1.3.1) which does not support hooks. Note: This may limit access to newer MkDocs features.

**Note**: Building documentation in CI/CD pipelines using `@techdocs/cli` does not mitigate this vulnerability, as the CLI uses the same vulnerable `@backstage/plugin-techdocs-node` package.

### References

[MkDocs Hooks Documentation](https://www.mkdocs.org/user-guide/configuration/#hooks)
[MkDocs 1.4 Release Notes](https://www.mkdocs.org/about/release-notes/#version-14-2022-09-27)
[TechDocs Architecture](https://backstage.io/docs/features/techdocs/architecture)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-6jr7-99pf-8vgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-25153
- https://github.com/backstage/backstage

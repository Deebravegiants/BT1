# [H] TechDocs Mkdocs Configuration Key Enables Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-928r-fm4v-mvrw
CVE: CVE-2026-29186
CWE: CWE-434, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-928r-fm4v-mvrw
Type: github-advisory

## Affected
- npm: `@backstage/plugin-techdocs-node` — affected >=0 <1.14.3

## Details
### Impact
This is a configuration bypass vulnerability that enables arbitrary code execution. The `@backstage/plugin-techdocs-node` package uses an allowlist to filter dangerous MkDocs configuration keys during the documentation build process. 

A gap in this allowlist allows attackers to craft an `mkdocs.yml` that causes arbitrary Python code execution, completely bypassing TechDocs' security controls.     

### Patches

Patched in `@backstage/plugin-techdocs-node` version 1.14.3

### Workarounds
If users cannot upgrade immediately:

1. Use Docker mode with restricted access: Configure TechDocs with `runIn: docker` instead of `runIn: local`. This provides container isolation, though it does not fully mitigate the risk.
2. Restrict repository access: Limit who can modify `mkdocs.yml` files in repositories that TechDocs processes. Only allow trusted contributors.
3. Manual review: Implement PR review requirements for changes to `mkdocs.yml` files to detect malicious hooks configurations before they are merged.
4. Downgrade MkDocs: Use MkDocs < 1.4.0 (e.g., 1.3.1) which does not support hooks. Note: This may limit access to newer MkDocs features.

Note: Building documentation in CI/CD pipelines using `@techdocs/cli` does not mitigate this vulnerability, as the CLI uses the same vulnerable `@backstage/plugin-techdocs-node` package.

### Resources
[MkDocs Hooks Documentation](https://www.mkdocs.org/user-guide/configuration/#hooks)
[MkDocs 1.4 Release Notes](https://www.mkdocs.org/about/release-notes/#version-14-2022-09-27)
[TechDocs Architecture](https://backstage.io/docs/features/techdocs/architecture)

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-928r-fm4v-mvrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-29186
- https://backstage.io/docs/features/techdocs/architecture
- https://github.com/backstage/backstage
- https://www.mkdocs.org/about/release-notes/#version-14-2022-09-27
- https://www.mkdocs.org/user-guide/configuration/#hooks

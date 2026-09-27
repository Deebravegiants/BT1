# [H] Storybook manager bundle may expose environment variables during build

## Summary
Severity: High
Advisory: GHSA-8452-54wp-rmv6
CVE: CVE-2025-68429
CWE: CWE-200, CWE-538, CWE-541
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-8452-54wp-rmv6
Type: github-advisory

## Affected
- npm: `storybook` — affected >=7.0.0 <7.6.21
- npm: `storybook` — affected >=8.0.0 <8.6.15
- npm: `storybook` — affected >=9.0.0 <9.1.17
- npm: `storybook` — affected >=10.0.0 <10.1.10

## Details
On December 11th, the Storybook team received a responsible disclosure alerting them to a potential vulnerability in certain built and published Storybooks. 

The vulnerability is a bug in how Storybook handles environment variables defined in a `.env` file, which could, in specific circumstances, lead to those variables being unexpectedly bundled into the artifacts created by the `storybook build` command. When a built Storybook is published to the web, the bundle’s source is viewable, thus potentially exposing those variables to anyone with access. If those variables contained secrets, they should be considered compromised.

## Who is impacted?

For a project to be vulnerable to this issue, it must:

- Build the Storybook (i.e. run `storybook build` directly or indirectly) in a directory that contains a `.env` file (including variants like `.env.local`)
- The `.env` file contains sensitive secrets
- Use Storybook version `7.0.0` or above
- Publish the built Storybook to the web

Storybooks built without a `.env` file at build time are not affected, including common CI-based builds where secrets are provided via platform environment variables rather than `.env` files.

Users' Storybook runtime environments (i.e. `storybook dev`) are not affected. Deployed applications that share a repo with a project's Storybook are not affected.

Storybook 6 and below are not affected.

## Recommended actions

First, Storybook recommends that everyone audit for any sensitive secrets provided via `.env` files and rotate those keys.

Second, Storybook has released patched versions of all affected major Storybook versions that no longer have this vulnerability. Projects should upgrade their Storybook—on both local machines and CI environments—to one of these versions **before publishing again**.

- `10.1.10+`
- `9.1.17+`
- `8.6.15+`
- `7.6.21+`

Finally, some projects may have been relying on the undocumented behavior at the heart of this issue and will need to change how they reference environment variables after this update. If a project can no longer read necessary environmental variable values, it can either prefix the variables with `STORYBOOK_` or use the [`env` property in Storybook’s configuration](https://storybook.js.org/docs/configure/environment-variables#using-storybook-configuration) to manually specify values. In either case, **do not** include sensitive secrets as they *will* be included in the built bundle.

## Further information

Details of the vulnerability can be found on the [Storybook announcement](https://storybook.js.org/blog/security-advisory).

## References
- https://github.com/storybookjs/storybook/security/advisories/GHSA-8452-54wp-rmv6
- https://nvd.nist.gov/vuln/detail/CVE-2025-68429
- https://github.com/storybookjs/storybook
- https://storybook.js.org/blog/security-advisory

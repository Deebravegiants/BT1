# [H] Packing does not respect root-level ignore files in workspaces

## Summary
Severity: High
Advisory: GHSA-hj9c-8jmm-8c52
CVE: CVE-2022-29244
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-02
Source: https://github.com/advisories/GHSA-hj9c-8jmm-8c52
Type: github-advisory

## Affected
- npm: `npm` — affected >=7.9.0 <8.11.0

## Details
### Impact
`npm pack` ignores root-level `.gitignore` & `.npmignore` file exclusion directives when run in a workspace or with a workspace flag (ie. `--workspaces`, `--workspace=<name>`). Anyone who has run `npm pack` or `npm publish` with workspaces, as of [v7.9.0](https://github.com/npm/cli/releases/tag/v7.9.0) & [v7.13.0](https://github.com/npm/cli/releases/tag/v7.13.0) respectively, may be affected and have published files into the npm registry they did not intend to include.

### Patch
- Upgrade to the latest, patched version of `npm` ([`v8.11.0`](https://github.com/npm/cli/releases/tag/v8.11.0) or greater), run: `npm i -g npm@latest`
- Node.js versions [`v16.15.1`](https://github.com/nodejs/node/releases/tag/v16.15.1), [`v17.19.1`](https://github.com/nodejs/node/releases/tag/v17.9.1) & [`v18.3.0`](https://github.com/nodejs/node/releases/tag/v18.3.0) include the patched `v8.11.0` version of `npm`

#### Steps to take to see if you're impacted
1. Run `npm publish --dry-run` or `npm pack` with an `npm` version `>=7.9.0` & `<8.11.0` inside the project's root directory using a workspace flag like: `--workspaces` or `--workspace=<name>` (ex. `npm pack --workspace=foo`)
2. Check the output in your terminal which will list the package contents (note: `tar -tvf <package-on-disk>` also works)
3. If you find that there are files included you did not expect, you should:
  3.1. Create & publish a new release excluding those files (ref. ["Keeping files out of your Package"](https://docs.npmjs.com/cli/v8/using-npm/developers#keeping-files-out-of-your-package))
  3.2. Deprecate the old package (ex. `npm deprecate <pkg>[@<version>] <message>`)
  3.3. Revoke or rotate any sensitive information (ex. passwords, tokens, secrets etc.) which might have been exposed
### References
- [CVE-2022-29244](https://nvd.nist.gov/vuln/detail/CVE-2022-29244)
- [`npm-packlist`](https://github.com/npm/npm-packlist)
- [`libnpmpack`](https://github.com/npm/cli/tree/latest/workspaces/libnpmpack)
- [`libnpmpublish`](https://github.com/npm/cli/tree/latest/workspaces/libnpmpublish)

## References
- https://github.com/npm/cli/security/advisories/GHSA-hj9c-8jmm-8c52
- https://nvd.nist.gov/vuln/detail/CVE-2022-29244
- https://github.com/nodejs/node/pull/43210
- https://github.com/nodejs/node/releases/tag/v16.15.1
- https://github.com/nodejs/node/releases/tag/v17.9.1
- https://github.com/nodejs/node/releases/tag/v18.3.0
- https://github.com/npm/cli
- https://github.com/npm/cli/releases/tag/v8.11.0
- https://github.com/npm/cli/tree/latest/workspaces/libnpmpack
- https://github.com/npm/cli/tree/latest/workspaces/libnpmpublish
- https://github.com/npm/npm-packlist
- https://security.netapp.com/advisory/ntap-20220722-0007

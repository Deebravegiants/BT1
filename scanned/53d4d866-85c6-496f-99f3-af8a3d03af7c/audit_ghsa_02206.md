# [H] UNIX Symbolic Link (Symlink) Following in @npmcli/arborist

## Summary
Severity: High
Advisory: GHSA-gmw6-94gg-2rc2
CVE: CVE-2021-39135
CWE: CWE-59, CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-31
Source: https://github.com/advisories/GHSA-gmw6-94gg-2rc2
Type: github-advisory

## Affected
- npm: `@npmcli/arborist` — affected >=0 <2.8.2

## Details
### Impact

Arbitrary File Creation, Arbitrary File Overwrite, Arbitrary Code Execution

`@npmcli/arborist`, the library that calculates dependency trees and manages the node_modules folder hierarchy for the npm command line interface, aims to guarantee that package dependency contracts will be met, and the extraction of package contents will always be performed into the expected folder.

This is accomplished by extracting package contents into a project's `node_modules` folder.

If the `node_modules` folder of the root project or any of its dependencies is somehow replaced with a symbolic link, it could allow Arborist to write package dependencies to any arbitrary location on the file system.

Note that symbolic links contained within package artifact contents are filtered out, so another means of creating a `node_modules` symbolic link would have to be employed.

1. A `preinstall` script could replace `node_modules` with a symlink.  (This is prevented by using `--ignore-scripts`.)
2. An attacker could supply the target with a git repository, instructing them to run `npm install --ignore-scripts` in the root.  This may be successful, because `npm install --ignore-scripts` is typically not capable of making changes outside of the project directory, so it may be deemed safe.

### Patches

2.8.2 (included in npm v7.20.7 and above)

### Workarounds

Do not run `npm install` on untrusted codebases, without first ensuring that the `node_modules` directory in the project is not a symbolic link.

### Fix

Prior to extracting any package contents, the `node_modules` folder into which it is extracted is verified to be a real directory.  If it is not, then it is removed.

Caveat: if you are currently relying on creating a symbolic link to the `node_modules` folder in order to share dependencies between projects, then that will no longer be possible.  Please use the `npm link` command, explicit `file:...` dependencies, and/or `workspaces` to share dependencies in a development environment.

## References
- https://github.com/npm/arborist/security/advisories/GHSA-gmw6-94gg-2rc2
- https://nvd.nist.gov/vuln/detail/CVE-2021-39135
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/npm/arborist
- https://www.npmjs.com/package/@npmcli/arborist
- https://www.oracle.com/security-alerts/cpuoct2021.html

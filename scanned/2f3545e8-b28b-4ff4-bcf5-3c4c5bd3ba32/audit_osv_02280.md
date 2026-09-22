# [H] ALPINE-CVE-2021-39135

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-39135
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-39135
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.22.6-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.6-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.17.6-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.17.6-r0

## Details
`@npmcli/arborist`, the library that calculates dependency trees and manages the node_modules folder hierarchy for the npm command line interface, aims to guarantee that package dependency contracts will be met, and the extraction of package contents will always be performed into the expected folder. This is accomplished by extracting package contents into a project's `node_modules` folder. If the `node_modules` folder of the root project or any of its dependencies is somehow replaced with a symbolic link, it could allow Arborist to write package dependencies to any arbitrary location on the file system. Note that symbolic links contained within package artifact contents are filtered out, so another means of creating a `node_modules` symbolic link would have to be employed. 1. A `preinstall` script could replace `node_modules` with a symlink. (This is prevented by using `--ignore-scripts`.) 2. An attacker could supply the target with a git repository, instructing them to run `npm install --ignore-scripts` in the root. This may be successful, because `npm install --ignore-scripts` is typically not capable of making changes outside of the project directory, so it may be deemed safe. This is patched in @npmcli/arborist 2.8.2 which is included in npm v7.20.7 and above. For more information including workarounds please see the referenced GHSA-gmw6-94gg-2rc2.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-39135

# [H] ALPINE-CVE-2021-39134

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-39134
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-39134
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
`@npmcli/arborist`, the library that calculates dependency trees and manages the `node_modules` folder hierarchy for the npm command line interface, aims to guarantee that package dependency contracts will be met, and the extraction of package contents will always be performed into the expected folder. This is, in part, accomplished by resolving dependency specifiers defined in `package.json` manifests for dependencies with a specific name, and nesting folders to resolve conflicting dependencies. When multiple dependencies differ only in the case of their name, Arborist's internal data structure saw them as separate items that could coexist within the same level in the `node_modules` hierarchy. However, on case-insensitive file systems (such as macOS and Windows), this is not the case. Combined with a symlink dependency such as `file:/some/path`, this allowed an attacker to create a situation in which arbitrary contents could be written to any location on the filesystem. For example, a package `pwn-a` could define a dependency in their `package.json` file such as `"foo": "file:/some/path"`. Another package, `pwn-b` could define a dependency such as `FOO: "file:foo.tgz"`. On case-insensitive file systems, if `pwn-a` was installed, and then `pwn-b` was installed afterwards, the contents of `foo.tgz` would be written to `/some/path`, and any existing contents of `/some/path` would be removed. Anyone using npm v7.20.6 or earlier on a case-insensitive filesystem is potentially affected. This is patched in @npmcli/arborist 2.8.2 which is included in npm v7.20.7 and above.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-39134

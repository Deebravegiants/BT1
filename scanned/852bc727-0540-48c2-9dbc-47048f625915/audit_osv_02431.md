# [C] ALPINE-CVE-2022-23521

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-23521
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23521
Type: osv

## Affected
- Alpine:v3.14: `git` — affected >=2.31.0 <2.32.5-r0
- Alpine:v3.15: `git` — affected >=2.31.0 <2.34.6-r0
- Alpine:v3.16: `git` — affected >=2.31.0 <2.36.4-r0
- Alpine:v3.17: `git` — affected >=2.31.0 <2.38.3-r0
- Alpine:v3.18: `git` — affected >=2.31.0 <2.39.1-r0
- Alpine:v3.19: `git` — affected >=2.31.0 <2.39.1-r0
- Alpine:v3.20: `git` — affected >=2.31.0 <2.39.1-r0
- Alpine:v3.21: `git` — affected >=2.31.0 <2.39.1-r0
- Alpine:v3.22: `git` — affected >=2.31.0 <2.39.1-r0
- Alpine:v3.23: `git` — affected >=2.31.0 <2.39.1-r0
- Alpine:v3.24: `git` — affected >=2.31.0 <2.39.1-r0

## Details
Git is distributed revision control system. gitattributes are a mechanism to allow defining attributes for paths. These attributes can be defined by adding a `.gitattributes` file to the repository, which contains a set of file patterns and the attributes that should be set for paths matching this pattern. When parsing gitattributes, multiple integer overflows can occur when there is a huge number of path patterns, a huge number of attributes for a single pattern, or when the declared attribute names are huge. These overflows can be triggered via a crafted `.gitattributes` file that may be part of the commit history. Git silently splits lines longer than 2KB when parsing gitattributes from a file, but not when parsing them from the index. Consequentially, the failure mode depends on whether the file exists in the working tree, the index or both. This integer overflow can result in arbitrary heap reads and writes, which may result in remote code execution. The problem has been patched in the versions published on 2023-01-17, going back to v2.30.7. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23521

# [M] ALPINE-CVE-2023-22490

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-22490
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-22490
Type: osv

## Affected
- Alpine:v3.14: `git` — affected >=2.31.0 <2.32.6-r0
- Alpine:v3.15: `git` — affected >=2.31.0 <2.34.7-r0
- Alpine:v3.16: `git` — affected >=2.31.0 <2.36.5-r0
- Alpine:v3.17: `git` — affected >=2.31.0 <2.38.4-r0
- Alpine:v3.18: `git` — affected >=2.31.0 <2.39.2-r0
- Alpine:v3.19: `git` — affected >=2.31.0 <2.39.2-r0
- Alpine:v3.20: `git` — affected >=2.31.0 <2.39.2-r0
- Alpine:v3.21: `git` — affected >=2.31.0 <2.39.2-r0
- Alpine:v3.22: `git` — affected >=2.31.0 <2.39.2-r0
- Alpine:v3.23: `git` — affected >=2.31.0 <2.39.2-r0
- Alpine:v3.24: `git` — affected >=2.31.0 <2.39.2-r0

## Details
Git is a revision control system. Using a specially-crafted repository, Git prior to versions 2.39.2, 2.38.4, 2.37.6, 2.36.5, 2.35.7, 2.34.7, 2.33.7, 2.32.6, 2.31.7, and 2.30.8 can be tricked into using its local clone optimization even when using a non-local transport. Though Git will abort local clones whose source `$GIT_DIR/objects` directory contains symbolic links, the `objects` directory itself may still be a symbolic link. These two may be combined to include arbitrary files based on known paths on the victim's filesystem within the malicious repository's working copy, allowing for data exfiltration in a similar manner as CVE-2022-39253.

A fix has been prepared and will appear in v2.39.2 v2.38.4 v2.37.6 v2.36.5 v2.35.7 v2.34.7 v2.33.7 v2.32.6, v2.31.7 and v2.30.8. If upgrading is impractical, two short-term workarounds are available. Avoid cloning repositories from untrusted sources with `--recurse-submodules`. Instead, consider cloning repositories without recursively cloning their submodules, and instead run `git submodule update` at each layer. Before doing so, inspect each new `.gitmodules` file to ensure that it does not contain suspicious module URLs.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-22490

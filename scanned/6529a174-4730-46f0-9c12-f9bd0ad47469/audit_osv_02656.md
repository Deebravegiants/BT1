# [C] ALPINE-CVE-2022-41903

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-41903
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41903
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
Git is distributed revision control system. `git log` can display commits in an arbitrary format using its `--format` specifiers. This functionality is also exposed to `git archive` via the `export-subst` gitattribute. When processing the padding operators, there is a integer overflow in `pretty.c::format_and_pad_commit()` where a `size_t` is stored improperly as an `int`, and then added as an offset to a `memcpy()`. This overflow can be triggered directly by a user running a command which invokes the commit formatting machinery (e.g., `git log --format=...`). It may also be triggered indirectly through git archive via the export-subst mechanism, which expands format specifiers inside of files within the repository during a git archive. This integer overflow can result in arbitrary heap writes, which may result in arbitrary code execution. The problem has been patched in the versions published on 2023-01-17, going back to v2.30.7. Users are advised to upgrade. Users who are unable to upgrade should disable `git archive` in untrusted repositories. If you expose git archive via `git daemon`, disable it by running `git config --global daemon.uploadArch false`.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41903

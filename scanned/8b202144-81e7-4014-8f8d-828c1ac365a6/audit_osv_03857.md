# [H] ALPINE-CVE-2026-57076

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-57076
Ecosystem: Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57076
Type: osv

## Affected
- Alpine:v3.24: `perl-yaml-syck` — affected >=0 <1.47-r0

## Details
YAML::Syck versions before 1.47 for Perl allow a heap use-after-free via an anchor name reused as an anchors-table key in syck_hdlr_add_anchor.

In the bundled libsyck an anchor name allocated by syck_strndup is stored both as node->anchor, freed when the node is freed, and as the key in the parser's anchors table. Freeing the node frees the shared key, and a later anchor redefinition makes st_delete compare against the freed key, so st_strcmp reads freed heap memory. Anchors are a standard YAML feature and need no special flags, so this is reached on the default Load path.

Any caller that runs Load or LoadFile on an untrusted document that redefines an anchor reaches the read of freed memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57076

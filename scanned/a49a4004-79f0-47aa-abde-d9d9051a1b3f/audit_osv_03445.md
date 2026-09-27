# [M] ALPINE-CVE-2026-13713

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-13713
Ecosystem: Alpine:v3.24
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-13713
Type: osv

## Affected
- Alpine:v3.24: `perl-yaml-syck` — affected >=0 <1.47-r0

## Details
YAML::Syck versions before 1.47 for Perl allow a use-after-free and double-free via an anchor node freed while still on the parser value stack.

In the bundled libsyck, when an anchor name is redefined or removed, syck_hdlr_add_anchor and syck_hdlr_remove_anchor free the node stored under that name with syck_free_node. That node can still be live on the parser's value stack, so syck_hdlr_add_node reaches it again and frees it a second time. On a normal build the 48-byte node chunk is freed twice and the interpreter aborts. Anchors need no special flags, so this is reached on the default Load path, and a 7-byte document that redefines an anchor triggers it.

Any caller that runs Load or LoadFile on an untrusted document that redefines an anchor mid-parse crashes the interpreter, a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-13713

# [M] YAML::Syck versions before 1.47 for Perl allow a use-after-free and double-free via an anchor node freed while still on the parser value stack

## Summary
Severity: Medium
Advisory: CVE-2026-13713
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-13713
Type: osv

## Details
YAML::Syck versions before 1.47 for Perl allow a use-after-free and double-free via an anchor node freed while still on the parser value stack.

In the bundled libsyck, when an anchor name is redefined or removed, syck_hdlr_add_anchor and syck_hdlr_remove_anchor free the node stored under that name with syck_free_node. That node can still be live on the parser's value stack, so syck_hdlr_add_node reaches it again and frees it a second time. On a normal build the 48-byte node chunk is freed twice and the interpreter aborts. Anchors need no special flags, so this is reached on the default Load path, and a 7-byte document that redefines an anchor triggers it.

Any caller that runs Load or LoadFile on an untrusted document that redefines an anchor mid-parse crashes the interpreter, a denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/07/17/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13713.json
- https://metacpan.org/release/TODDR/YAML-Syck-1.47/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-13713
- https://github.com/toddr/YAML-Syck/commit/44c90a109ec3215ee7ce747bd11209835e123d8b.patch
- https://github.com/toddr/YAML-Syck

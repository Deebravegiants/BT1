# [M] Unbounded memory allocation in highlight_lines range expansion in mdex

## Summary
Severity: Medium
Advisory: CVE-2026-53428
Aliases: EEF-CVE-2026-53428, GHSA-j93q-9cvj-rxfm
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-53428
Type: osv

## Details
Memory Allocation with Excessive Size Value vulnerability in leandrocp mdex allows an unauthenticated attacker to cause a denial of service through unbounded memory allocation.

comrak_nif::lumis_adapter::LumisAdapter::parse_highlight_lines in native/comrak_nif/src/lumis_adapter.rs eagerly expands a user-controlled inclusive line range from a fenced code block's highlight_lines decorator into a Vec<usize>, pushing one element per integer in the range with no upper bound on the range size. An attacker who can supply Markdown that an application renders with MDEx.to_html/2 (for example a comment, chat message, or wiki page) can embed a code block whose info string is rust highlight_lines="1-100000000", forcing the native adapter to allocate roughly 8 bytes per line in the range.

A payload that differs by only a few bytes can therefore allocate hundreds of megabytes, and a sufficiently large range (for example 1-2000000000) exhausts host memory and aborts the BEAM, denying service to every user of the rendering process. The per-line write loop additionally tests membership with a linear scan over the same vector, degrading rendering to a quadratic cost even for ranges that do not immediately exhaust memory.

The vulnerable native code originally shipped inside mdex (in native/comrak_nif/src/lumis_adapter.rs) and was later extracted into the separate mdex_native package (native/mdex_native_nif/src/lumis_adapter.rs), where it remains unpatched.

This issue affects mdex from 0.11.0 before 0.12.3, and mdex_native from 0.1.0 before 0.2.3.

## References
- https://cna.erlef.org/cves/CVE-2026-53428.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-53428
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53428.json
- https://github.com/leandrocp/mdex_native/security/advisories/GHSA-j93q-9cvj-rxfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53428
- https://github.com/leandrocp/mdex_native/commit/798a363b4339f6f7162ec8437c4c9f9b5ae6fbf3
- https://github.com/leandrocp/mdex
- https://github.com/leandrocp/mdex_native

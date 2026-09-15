# [M] Unbounded native memory leak in mdex escaped-tag rendering enables unauthenticated denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-53429
Aliases: EEF-CVE-2026-53429, GHSA-cmvp-gp9f-23xw
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-53429
Type: osv

## Details
Missing Release of Memory after Effective Lifetime vulnerability in leandrocp mdex and mdex_native allows an attacker who controls a rendered document to cause a denial of service through unbounded native memory exhaustion.

The native rendering code permanently leaks memory when rendering a document that contains escaped-tag nodes. The conversion of each %MDEx.EscapedTag{} node into its native representation (From<ExEscapedTag> for NodeValue in the Rust NIF) calls Box::leak on the caller-supplied literal string, which surrenders the backing allocation so that it lives for the entire lifetime of the operating system process and is never freed.

Both the byte length of each literal and the number of escaped-tag nodes in a document are attacker-controlled, and there is no size cap, rate limit, or string interning on this path. Every render of a document containing escaped-tag nodes therefore leaks literal_size x node_count bytes that can never be reclaimed, and repeated renders accumulate without bound. Rendering reaches this path through the public MDEx.to_html/1 entry point and any other API that renders a supplied %MDEx.Document{}.

Any application that uses mdex (or mdex_native directly) to render documents derived from user-supplied content is affected. Because the leaked memory is never reclaimed for the life of the BEAM process, an attacker can drive resident memory upward without limit until the node exhausts memory and crashes, taking down every process on it.

The vulnerable native code originally shipped inside mdex (in native/comrak_nif/src/types/document.rs) and was later extracted into the separate mdex_native package (native/mdex_native_nif/src/types/document.rs), where it remains unpatched.

This issue affects mdex from 0.11.0 before 0.12.3, and mdex_native from 0.1.0 before 0.2.3.

## References
- https://cna.erlef.org/cves/CVE-2026-53429.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-53429
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53429.json
- https://github.com/leandrocp/mdex_native/security/advisories/GHSA-cmvp-gp9f-23xw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53429
- https://github.com/leandrocp/mdex_native/commit/cbd927fb5061b488de8d90a8ef6df65718ca1fe6
- https://github.com/leandrocp/mdex
- https://github.com/leandrocp/mdex_native

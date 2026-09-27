# [H] JavaScript::Minifier::XS versions before 0.16 for Perl leak memory on every call to minify(), allowing unbounded memory growth

## Summary
Severity: High
Advisory: CVE-2026-56018
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-56018
Type: osv

## Details
JavaScript::Minifier::XS versions before 0.16 for Perl leak memory on every call to minify(), allowing unbounded memory growth.

In JsMinify (XS.xs) the cleanup frees only the NodeSet structures and never the per-token contents buffers allocated in JsSetNodeContents; JsDiscardNode unlinks nodes without freeing their contents. Each token's contents buffer is therefore leaked on every call, and the two early returns taken when the node list is empty leak the whole NodeSet.

A long-lived process that minifies repeatedly, such as an asset pipeline or a server-side minifier endpoint, grows in memory without bound until it exhausts available memory and is killed, causing denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/17
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56018.json
- https://metacpan.org/release/GTERMARS/JavaScript-Minifier-XS-0.16/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-56018
- https://github.com/bleargh45/JavaScript-Minifier-XS/issues/10
- https://github.com/bleargh45/JavaScript-Minifier-XS

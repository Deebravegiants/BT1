# [M] TeX Live SyncTeX Parser Heap Use-After-Free via Malformed SyncTeX File

## Summary
Severity: Medium
Advisory: CVE-2026-63729
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-63729
Type: osv

## Details
The SyncTeX parser (synctex_parser.c) shipped with TeX Live and embedded by downstream consumers such as GNOME Evince contains a heap use-after-free vulnerability that allows attackers to crash applications or potentially execute arbitrary code by supplying a malformed .synctex or .synctex.gz file. A malformed SyncTeX file can construct a ref node with a NULL parent pointer, causing the replacement routine to fail to detach the node from its sibling chain, which triggers recursive freeing of live tree nodes and leaves dangling pointers that are later accessed by the parser during document load.

## References
- https://fatihhcelik.github.io/posts/evince-synctex-heap-use-after-free/
- https://github.com/TeX-Live/texlive-source/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63729.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63729
- https://www.vulncheck.com/advisories/tex-live-synctex-parser-heap-use-after-free-via-malformed-synctex-file
- https://github.com/TeX-Live/texlive-source/commit/002dcd3eac30db5c352f53d4181737961cc7ee9a

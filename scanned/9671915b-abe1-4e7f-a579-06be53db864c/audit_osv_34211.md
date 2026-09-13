# [H] CVE-2025-55780

## Summary
Severity: High
Advisory: CVE-2025-55780
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-55780
Type: osv

## Details
A null pointer dereference occurs in the function break_word_for_overflow_wrap() in MuPDF 1.26.4 when rendering a malformed EPUB document. Specifically, the function calls fz_html_split_flow() to split a FLOW_WORD node, but does not check if node->next is valid before accessing node->next->overflow_wrap, resulting in a crash if the split fails or returns a partial node chain.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=708720
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=bdd5d241748807378a78a622388e0312332513c5
- https://github.com/ISH2YU/CVE-2025-55780/tree/main
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55780.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55780

# [M] Courier IMAP < 6.0.1 Mail Server < 2.0.2 Stack Overflow DoS via Nested SEARCH Queries

## Summary
Severity: Medium
Advisory: CVE-2026-67194
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-67194
Type: osv

## Details
Courier IMAP before 6.0.1 and Courier Mail Server before 2.0.2 allow authenticated IMAP users to crash the imapd process via deeply nested parenthesized SEARCH queries. The SEARCH command parser (alloc_search_key in searchinfo.C) recursively descends on nested parenthesized groups through a mutual recursion chain with alloc_search_andlist() and alloc_search_notkey(), with no depth limit. Courier IMAP has no overall command line length limit, making exploitation trivial. A single IMAP command with ~2500 nested parentheses overflows the 8MB default stack, causing SIGSEGV.

## References
- https://packages.debian.org/sid/courier-imap
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67194.json
- https://github.com/svarshavchik/courier/releases/tag/courier%2F2.0.2%2F20260627214309
- https://github.com/svarshavchik/courier/releases/tag/courier-imap%2F6.0.1%2F20260627214444
- https://nvd.nist.gov/vuln/detail/CVE-2026-67194
- https://www.vulncheck.com/advisories/courier-imap-mail-server-stack-overflow-dos-via-nested-search-queries
- https://github.com/svarshavchik/courier-libs/commit/b5b5581aabea3efadf5e2944947ff0214aa3533e
- https://github.com/svarshavchik/courier

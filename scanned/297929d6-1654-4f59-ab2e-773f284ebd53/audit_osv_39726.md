# [M] Tiptap for PHP < 2.1.1 DoS via Malformed href Attribute

## Summary
Severity: Medium
Advisory: CVE-2026-47110
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-47110
Type: osv

## Details
Tiptap for PHP before version 2.1.1 contains an input validation vulnerability that allows authenticated attackers to cause a denial of service by submitting Tiptap JSON with the attrs.href field set to an array instead of a string, causing an unhandled TypeError in the Link::isAllowedUri() function when passed to preg_match(). Attackers can persist malformed JSON records that permanently crash the server-side HTML rendering pipeline for all subsequent viewers of that record until the database entry is manually repaired.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47110.json
- https://github.com/ueberdosis/tiptap-php/releases/tag/2.1.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-47110
- https://www.vulncheck.com/advisories/tiptap-for-php-dos-via-malformed-href-attribute
- https://github.com/ueberdosis/tiptap-php/pull/94
- https://github.com/ueberdosis/tiptap-php/commit/74bfb7be1c8c6102b240f3879b7f984a6ab87b97
- https://github.com/ueberdosis/tiptap-php

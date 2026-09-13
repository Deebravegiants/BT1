# [C] Vim: Heap Buffer Overflow in Text Property Handling

## Summary
Severity: Critical
Advisory: CVE-2026-73074
Aliases: GHSA-hm4g-pjfx-m27j
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73074
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0841, prop_add_one() in src/textprop.c uses the proplen value from get_text_props() to increment a uint16_t property count beyond 0xffff, wrapping the count to zero and copying existing text-property records into a heap allocation sized for none of them. This issue is fixed in version 9.2.0841.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73074.json
- https://github.com/vim/vim/security/advisories/GHSA-hm4g-pjfx-m27j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73074
- https://github.com/vim/vim/commit/a9336b476fd1a182e3f79b5f83c0ffb04f8a922b

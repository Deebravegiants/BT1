# [H] Kitty has a Heap Buffer Overflow in its Graphics Protocol Handler

## Summary
Severity: High
Advisory: CVE-2026-33633
Aliases: GHSA-j68c-v8x4-269g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-33633
Type: osv

## Details
Kitty is a cross-platform GPU based terminal. Versions 0.46.2 and below contain a heap buffer overflow in load_image_data() that allows any process which can write to the terminal's stdin to crash kitty immediately. The vulnerability is triggered by a single APC graphics protocol command with a PNG format declaration (f=100) whose payload exceeds twice the initial buffer capacity. The overflow is attacker-controlled in both length and content, causing DoS and potentially escalation to RCE itself. This issue has been fixed in version 0.47.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33633.json
- https://github.com/kovidgoyal/kitty/security/advisories/GHSA-j68c-v8x4-269g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33633
- https://github.com/kovidgoyal/kitty/commit/e9661f0f3afb4e4dbffa509adfb3df3c9780ad34

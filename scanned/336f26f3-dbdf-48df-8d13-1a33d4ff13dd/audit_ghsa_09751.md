# [M] FastChat has a Content Moderation Bypass via Arena Side-by-Side Views

## Summary
Severity: Medium
Advisory: GHSA-f3q6-69f3-vwch
CVE: CVE-2026-6608
CWE: CWE-670
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-f3q6-69f3-vwch
Type: github-advisory

## Affected
- PyPI: `fschat` — affected >=0

## Details
A vulnerability was detected in lm-sys fastchat up to 0.2.36. Impacted is the function add_text of the component Arena Side-by-Side View Handler. The manipulation results in incorrect control flow. The attack can be launched remotely. The exploit is now public and may be used. The root cause was fixed in commit 34eca62 for gradio_block_arena_named.py, but three other files were missed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6608
- https://github.com/lm-sys/FastChat/issues/3834
- https://gist.github.com/YLChen-007/e45039d23e698222d887ee09735d9d36
- https://github.com/lm-sys/FastChat
- https://vuldb.com/submit/792228
- https://vuldb.com/vuln/358243
- https://vuldb.com/vuln/358243/cti

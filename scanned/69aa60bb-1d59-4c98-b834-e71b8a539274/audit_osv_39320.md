# [M] Vim: Heap Buffer Overflow in spell file loading

## Summary
Severity: Medium
Advisory: CVE-2026-45130
Aliases: GHSA-q4jv-r9gj-6cwv
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-45130
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0450, a heap buffer overflow exists in read_compound() in src/spellfile.c when loading a crafted spell file (.spl) with UTF-8 encoding active. An attacker-controlled length field in the spell file's compound section overflows a 32-bit signed integer multiplication, causing a small buffer to be allocated for a write loop that runs many iterations, overflowing the heap. Because the 'spelllang' option can be set from a modeline, a text file modeline can trigger spell file loading if a malicious .spl file has been planted on the runtimepath. This issue has been patched in version 9.2.0450.

## References
- http://www.openwall.com/lists/oss-security/2026/05/14/3
- https://github.com/vim/vim/releases/tag/v9.2.0450
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45130.json
- https://github.com/vim/vim/security/advisories/GHSA-q4jv-r9gj-6cwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45130
- https://github.com/vim/vim/commit/92993329178cb1f72d700fff45ca86e1c2d369f8

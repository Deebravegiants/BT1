# [H] CVE-2019-14452

## Summary
Severity: High
Advisory: CVE-2019-14452
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-14452
Type: osv

## Details
Sigil before 0.9.16 is vulnerable to a directory traversal, allowing attackers to write arbitrary files via a ../ (dot dot slash) in a ZIP archive entry that is mishandled during extraction.

## References
- https://salvatoresecurity.com/zip-slip-in-sigil-cve-2019-14452/
- https://github.com/Sigil-Ebook/Sigil/compare/ea7f27d...5b867e5
- https://github.com/Sigil-Ebook/Sigil/releases/tag/0.9.16
- https://github.com/Sigil-Ebook/flightcrew/issues/52#issuecomment-505967936
- https://github.com/Sigil-Ebook/flightcrew/issues/52#issuecomment-505997355
- https://usn.ubuntu.com/4085-1/
- https://github.com/Sigil-Ebook/Sigil/commit/04e2f280cc4a0766bedcc7b9eb56449ceecc2ad4
- https://github.com/Sigil-Ebook/Sigil/commit/0979ba8d10c96ebca330715bfd4494ea0e019a8f
- https://github.com/Sigil-Ebook/Sigil/commit/369eebe936e4a8c83cc54662a3412ce8bef189e4

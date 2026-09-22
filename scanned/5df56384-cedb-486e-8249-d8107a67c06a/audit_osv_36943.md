# [H] SAIL: Heap-based Buffer Overflow in Sail-codecs-xwd

## Summary
Severity: High
Advisory: CVE-2026-27168
Aliases: GHSA-3g38-x2pj-mv55
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-27168
Type: osv

## Details
SAIL is a cross-platform library for loading and saving images with support for animation, metadata, and ICC profiles. All versions are vulnerable to Heap-based Buffer Overflow through the XWD parser's use of the bytes_per_line value. The value os read directly from the file as the read size in io->strict_read(), and is never compared to the actual size of the destination buffer. An attacker can provide an XWD file with an arbitrarily large bytes_per_line, causing a massive write operation beyond the buffer heap allocated for the image pixels. The issue did not have a fix at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27168.json
- https://github.com/HappySeaFox/sail/security/advisories/GHSA-3g38-x2pj-mv55
- https://nvd.nist.gov/vuln/detail/CVE-2026-27168

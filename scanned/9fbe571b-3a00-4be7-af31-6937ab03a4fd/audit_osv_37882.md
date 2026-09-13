# [H] Zserio: Integer Overflow in BitStreamReader on 32-bit platforms

## Summary
Severity: High
Advisory: CVE-2026-33666
Aliases: GHSA-fjwv-6wcr-vqwj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-33666
Type: osv

## Details
Zserio is a framework for serializing structured data with a compact and efficient way with low overhead. Prior to 2.18.1, in BitStreamReader.h readBytes() / readString(), the setBitPosition() bounds check receives the overflowed value and is completely bypassed. The code then reads len bytes (512 MB) from a buffer that is only a few bytes long, causing a segmentation fault. This vulnerability is fixed in 2.18.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33666.json
- https://github.com/ndsev/zserio/security/advisories/GHSA-fjwv-6wcr-vqwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33666

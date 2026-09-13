# [M] NanaZip: Heap out-of-bounds read in NanaZip AVB hashtree descriptor parser via 32-bit unsigned integer overflow

## Summary
Severity: Medium
Advisory: CVE-2026-47223
Aliases: GHSA-qhc5-mh6j-4g75
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47223
Type: osv

## Details
NanaZip is the 7-Zip derivative intended for the modern Windows experience. From version 3.0.1000.0 to before version 6.0.1698.0, a heap out-of-bounds read exists in the Android Verified Boot (AVB) vbmeta image parser in NanaZip (via the upstream 7-Zip AvbHandler). A 32-bit unsigned integer overflow in the bounds check pos + ht.salt_len > descSize allows an attacker-controlled salt_len field to bypass validation, causing CByteBuffer::CopyFrom to memcpy up to ~4 GiB past the end of a 64. This issue has been patched in stable version 6.0.1698.0 and preview version 6.5.1742.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47223.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-qhc5-mh6j-4g75
- https://nvd.nist.gov/vuln/detail/CVE-2026-47223

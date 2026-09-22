# [M] CVE-2025-70101

## Summary
Severity: Medium
Advisory: CVE-2025-70101
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2025-70101
Type: osv

## Details
An out-of-bounds read in the ext4_ext_binsearch_idx function in src/ext4_extent.c of the lwext4 1.0.0 library allows attackers to cause a denial of service by supplying a specially crafted ext4 filesystem image. The vulnerability occurs due to insufficient validation of extent header fields before performing a binary search over extent index entries, which can result in invalid pointer calculations and an out-of-bounds memory read during extent tree traversal.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/6
- https://github.com/sigdevel/pocs/blob/main/res/lwext4/3/sig11_lwext4_ext4_extent_815
- https://infosec.exchange/@sigdevel/116668958927817708
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70101.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70101
- https://github.com/gkostka/lwext4/issues/91

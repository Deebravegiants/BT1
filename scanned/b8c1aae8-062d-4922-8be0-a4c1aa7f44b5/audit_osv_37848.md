# [M] Apache Answer: Uploading specially crafted TIFF files causes an Out-of-Memory error

## Summary
Severity: Medium
Advisory: CVE-2026-33582
Aliases: GHSA-v553-g2w6-295p, GO-2026-6153
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-33582
Type: osv

## Details
Unrestricted Upload of File with Dangerous Type vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

A crafted TIFF image could trigger excessive memory allocation during image decoding, allowing an authenticated user to cause the server process to crash.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/09/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33582.json
- https://lists.apache.org/thread/3sgpx4cwsgpnt66xv3cqvtc8z4st1kbq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33582

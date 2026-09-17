# [H] CVE-2025-65844

## Summary
Severity: High
Advisory: CVE-2025-65844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-12-02
Source: https://osv.dev/vulnerability/CVE-2025-65844
Type: osv

## Details
EverShop 2.0.1 allows a remote unauthenticated attacker to upload arbitrary files and create directories via the /api/images endpoint. The endpoint is accessible without authentication by default, and server-side validation of uploaded files is insufficient. This can be abused to upload arbitrary content (including non-image files) which could impersonate user/admin login panels (exfiltrating credentials) and to perform a denial-of-service attack by exhausting disk space.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65844.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65844
- https://github.com/evershopcommerce/evershop/issues/819

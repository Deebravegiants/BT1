# [M] leancrypto: Integer truncation in X.509 name parser enables certificate identity impersonation

## Summary
Severity: Medium
Advisory: CVE-2026-34610
Aliases: GHSA-636g-jxv4-v4gr
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34610
Type: osv

## Details
The leancrypto library is a cryptographic library that exclusively contains only PQC-resistant cryptographic algorithms. Prior to version 1.7.1, lc_x509_extract_name_segment() casts size_t vlen to uint8_t when storing the Common Name (CN) length. An attacker who crafts a certificate with CN = victim's CN + 256 bytes padding gets cn_size = (uint8_t)(256 + N) = N, where N is the victim's CN length. The first N bytes of the attacker's CN are the victim's identity. After parsing, the attacker's certificate has an identical CN to the victim's — enabling identity impersonation in PKCS#7 verification, certificate chain matching, and code signing. This issue has been patched in version 1.7.1.

## References
- https://github.com/smuellerDD/leancrypto/releases/tag/v1.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34610.json
- https://github.com/smuellerDD/leancrypto/security/advisories/GHSA-636g-jxv4-v4gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34610
- https://github.com/smuellerDD/leancrypto/commit/5cdcbe12bd6c3d6e87e969972a580b44a74c3a6a

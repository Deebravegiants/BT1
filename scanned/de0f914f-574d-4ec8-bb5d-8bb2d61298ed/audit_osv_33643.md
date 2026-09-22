# [H] CVE-2025-47917

## Summary
Severity: High
Advisory: CVE-2025-47917
CVSS: 8.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:H)
Published: 2025-07-20
Source: https://osv.dev/vulnerability/CVE-2025-47917
Type: osv

## Details
Mbed TLS before 3.6.4 allows a use-after-free in certain situations of applications that are developed in accordance with the documentation. The function mbedtls_x509_string_to_names() takes a head argument that is documented as an output argument. The documentation does not suggest that the function will free that pointer; however, the function does call mbedtls_asn1_free_named_data_list() on that argument, which performs a deep free(). As a result, application code that uses this function (relying only on documented behavior) is likely to still hold pointers to the memory blocks that were freed, resulting in a high risk of use-after-free or double-free. In particular, the two sample programs x509/cert_write and x509/cert_req are affected (use-after-free if the san string contains more than one DN).

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00013.html
- https://lists.debian.org/debian-lts-announce/2025/08/msg00025.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47917.json
- https://github.com/Mbed-TLS/mbedtls-docs/blob/main/security-advisories/mbedtls-security-advisory-2025-06-7.md
- https://mbed-tls.readthedocs.io/en/latest/tech-updates/security-advisories/
- https://nvd.nist.gov/vuln/detail/CVE-2025-47917

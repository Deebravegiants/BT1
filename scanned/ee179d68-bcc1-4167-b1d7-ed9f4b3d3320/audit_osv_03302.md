# [C] ALPINE-CVE-2025-47917

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-47917
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-47917
Type: osv

## Affected
- Alpine:v3.20: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.21: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.22: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.23: `mbedtls` — affected >=0 <3.6.4-r0
- Alpine:v3.24: `mbedtls` — affected >=0 <3.6.4-r0

## Details
Mbed TLS before 3.6.4 allows a use-after-free in certain situations of applications that are developed in accordance with the documentation. The function mbedtls_x509_string_to_names() takes a head argument that is documented as an output argument. The documentation does not suggest that the function will free that pointer; however, the function does call mbedtls_asn1_free_named_data_list() on that argument, which performs a deep free(). As a result, application code that uses this function (relying only on documented behavior) is likely to still hold pointers to the memory blocks that were freed, resulting in a high risk of use-after-free or double-free. In particular, the two sample programs x509/cert_write and x509/cert_req are affected (use-after-free if the san string contains more than one DN).

## References
- https://security.alpinelinux.org/vuln/CVE-2025-47917

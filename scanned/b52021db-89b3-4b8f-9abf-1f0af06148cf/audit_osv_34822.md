# [M] CVE-2025-65498

## Summary
Severity: Medium
Advisory: CVE-2025-65498
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65498
Type: osv

## Details
NULL pointer dereference in coap_dtls_generate_cookie() in src/coap_openssl.c in OISM libcoap 4.3.5 allows remote attackers to cause a denial of service via a crafted DTLS handshake that triggers SSL_get_SSL_CTX() to return NULL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65498.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65498
- https://github.com/obgm/libcoap/issues/1746
- https://github.com/obgm/libcoap/pull/1750

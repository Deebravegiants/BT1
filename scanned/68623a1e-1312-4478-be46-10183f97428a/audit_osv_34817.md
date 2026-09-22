# [H] CVE-2025-65493

## Summary
Severity: High
Advisory: CVE-2025-65493
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65493
Type: osv

## Details
NULL pointer dereference in src/coap_openssl.c in OISM libcoap 4.3.5 allows remote attackers to cause a denial of service via a crafted DTLS/TLS connection that triggers BIO_get_data() to return NULL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65493.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65493
- https://github.com/obgm/libcoap/issues/1743
- https://github.com/obgm/libcoap/pull/1750

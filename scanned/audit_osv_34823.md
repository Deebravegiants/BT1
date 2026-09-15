# [M] CVE-2025-65499

## Summary
Severity: Medium
Advisory: CVE-2025-65499
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65499
Type: osv

## Details
Array index error in tls_verify_call_back() in src/coap_openssl.c in OISM libcoap 4.3.5 allows remote attackers to cause a denial of service via a crafted DTLS handshake that triggers SSL_get_ex_data_X509_STORE_CTX_idx() to return -1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65499.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65499
- https://github.com/obgm/libcoap/issues/1747
- https://github.com/obgm/libcoap/pull/1750

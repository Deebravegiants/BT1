# [M] CVE-2025-65501

## Summary
Severity: Medium
Advisory: CVE-2025-65501
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65501
Type: osv

## Details
Null pointer dereference in coap_dtls_info_callback() in OISM libcoap 4.3.5 allows remote attackers to cause a denial of service via a DTLS handshake where SSL_get_app_data() returns NULL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65501.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65501
- https://github.com/obgm/libcoap/issues/1748
- https://github.com/obgm/libcoap/pull/1750

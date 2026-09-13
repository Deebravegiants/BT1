# [H] CVE-2025-65495

## Summary
Severity: High
Advisory: CVE-2025-65495
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65495
Type: osv

## Details
Integer signedness error in tls_verify_call_back() in src/coap_openssl.c in OISM libcoap 4.3.5 allows remote attackers to cause a denial of service via a crafted TLS certificate that causes i2d_X509() to return -1 and be misused as a malloc() size parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65495.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65495
- https://github.com/obgm/libcoap/issues/1744
- https://github.com/obgm/libcoap/pull/1750

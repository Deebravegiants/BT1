# [H] CVE-2025-65494

## Summary
Severity: High
Advisory: CVE-2025-65494
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-24
Source: https://osv.dev/vulnerability/CVE-2025-65494
Type: osv

## Details
NULL pointer dereference in get_san_or_cn_from_cert() in src/coap_openssl.c in OISM libcoap 4.3.5 allows remote attackers to cause a denial of service via a crafted X.509 certificate that causes sk_GENERAL_NAME_value() to return NULL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65494.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65494
- https://github.com/obgm/libcoap/issues/1745
- https://github.com/obgm/libcoap/pull/1750

# [M] CVE-2025-59391

## Summary
Severity: Medium
Advisory: CVE-2025-59391
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-59391
Type: osv

## Details
A memory disclosure vulnerability exists in libcoap's OSCORE configuration parser in libcoap before release-4.3.5-patches. An out-of-bounds read may occur when parsing certain configuration values, allowing an attacker to infer or read memory beyond string boundaries in the .rodata section. This could potentially lead to information disclosure or denial of service.

## References
- https://github.com/obgm/libcoap/releases/tag/v4.3.5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59391.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59391
- https://github.com/obgm/libcoap/pull/1730

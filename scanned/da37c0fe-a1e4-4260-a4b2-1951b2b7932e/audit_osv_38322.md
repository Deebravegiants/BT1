# [H] CVE-2026-38821

## Summary
Severity: High
Advisory: CVE-2026-38821
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-38821
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in openNDS before 11.0.0 that allows an unauthenticated attacker on the captive portal network to crash the openNDS daemon (denial of service) and potentially achieve remote code execution. This is in http_microhttpd.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38821.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38821
- https://github.com/openNDS/openNDS/commit/3b5f7ef40cd048826d3c4a16f61a73a1768fd5a9

# [C] CVE-2024-48406

## Summary
Severity: Critical
Advisory: CVE-2024-48406
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-48406
Type: osv

## Details
Buffer Overflow vulnerability in SunBK201 umicat through v.0.3.2 and fixed in v.0.3.3 allows an attacker to execute arbitrary code via the power(uct_int_t x, uct_int_t n) in src/uct_upstream.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48406.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48406
- https://github.com/SunBK201/umicat/issues/2
- https://github.com/SunBK201/umicat/pull/3

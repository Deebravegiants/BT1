# [M] CVE-2023-45919

## Summary
Severity: Medium
Advisory: CVE-2023-45919
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-45919
Type: osv

## Details
Mesa 23.0.4 was discovered to contain a buffer over-read in glXQueryServerString(). NOTE: this is disputed because there are no common situations in which users require uninterrupted operation with an attacker-controller server.

## References
- http://packetstormsecurity.com/files/176802/Mesa-23.0.4-Buffer-Overflow.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45919.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-45919
- https://gitlab.freedesktop.org/mesa/mesa/-/issues/9858
- http://seclists.org/fulldisclosure/2024/Jan/47

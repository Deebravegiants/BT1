# [H] CVE-2024-24263

## Summary
Severity: High
Advisory: CVE-2024-24263
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24263
Type: osv

## Details
Lotos WebServer v0.1.1 was discovered to contain a Use-After-Free (UAF) vulnerability via the response_append_status_line function at /lotos/src/response.c.

## References
- https://github.com/LuMingYinDetect/lotos_detects/blob/main/lotos_detect_1.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24263.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-24263

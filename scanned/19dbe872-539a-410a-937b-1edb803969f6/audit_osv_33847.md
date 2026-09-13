# [H] CVE-2025-51495

## Summary
Severity: High
Advisory: CVE-2025-51495
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-51495
Type: osv

## Details
An integer overflow vulnerability exists in the WebSocket component of Mongoose 7.5 thru 7.17. By sending a specially crafted WebSocket request, an attacker can cause the application to crash. If downstream vendors integrate this component improperly, the issue may lead to a buffer overflow.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51495.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51495
- https://github.com/cesanta/mongoose/pull/3131
- https://github.com/cainiao159357/CVE-2025-51495
- https://github.com/cesanta/mongoose
